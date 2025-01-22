import os
import requests
import zipfile
import tkinter as tk
from tkinter import ttk, messagebox
import shutil
import psutil
import threading

# URL del repositori
REPO_URL = "https://github.com/aemon1977/Dinamic-apk"
ZIP_URL = f"{REPO_URL}/archive/refs/heads/main.zip"  # URL per al fitxer ZIP
DESTINATION_FOLDER = "C:\\Dinamic"
UPDATER_FOLDER = "C:\\Dinamic\\updater"
VERSION_FILE = os.path.join(DESTINATION_FOLDER, "version.txt")

# Funció per llegir la versió actual des del fitxer
def get_current_version():
    if os.path.exists(VERSION_FILE):
        with open(VERSION_FILE, 'r') as file:
            return file.read().strip()  # Llegeix la versió i elimina espais en blanc
    return None

# Funció per tancar altres processos de Python
def close_other_python_processes():
    current_pid = os.getpid()  # Obtenir l'ID del procés actual
    for proc in psutil.process_iter(['pid', 'name']):
        if proc.info['name'] == 'python.exe' and proc.info['pid'] != current_pid:
            try:
                proc.terminate()  # Terminar el procés
                proc.wait()  # Esperar a que el procés es tanqui
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass  # Ignorar errors si el procés ja no existeix o no es pot accedir

# Funció per esborrar fitxers a la carpeta de destí, excepte les carpetes especificades
def clear_destination_folder():
    for item in os.listdir(DESTINATION_FOLDER):
        item_path = os.path.join(DESTINATION_FOLDER, item)
        
        # Verificar si és un directori i si no és un dels que volem conservar
        if os.path.isdir(item_path) and item not in ['actualizador', 'mysql']:
            shutil.rmtree(item_path)  # Esborrar la carpeta i el seu contingut
        elif os.path.isfile(item_path):
            os.remove(item_path)  # Esborrar el fitxer

# Funció per descarregar el fitxer
def download_file(url, destination):
    response = requests.get(url, stream=True)
    total_size = int(response.headers.get('content-length', 0))  # Pot ser 0 si no es proporciona

    if total_size == 0:
        # Si no es pot determinar la mida, usar barra de progrés indeterminada
        progress_bar['mode'] = 'indeterminate'
        progress_bar.start()
    
    # Assegurar-se que el directori de destí existeixi
    os.makedirs(os.path.dirname(destination), exist_ok=True)

    with open(destination, 'wb') as file:
        downloaded_size = 0
        for data in response.iter_content(chunk_size=4096):
            file.write(data)
            downloaded_size += len(data)
            if total_size > 0:
                progress_bar['value'] = (downloaded_size / total_size) * 100
            root.update_idletasks()

    # Aturar la barra de progrés indeterminada si s'estava utilitzant
    if total_size == 0:
        progress_bar.stop()
        progress_bar['mode'] = 'determinate'
        progress_bar['value'] = 100  # Completar la barra de progrés

    # Verificar si es va descarregar un fitxer ZIP vàlid
    if not zipfile.is_zipfile(destination):
        raise ValueError("El fitxer descarregat no és un fitxer ZIP vàlid.")

# Funció per extreure el fitxer i moure només el contingut a la carpeta de destí
def extract_zip(zip_path, extract_to):
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        # Extreure tots els fitxers a una carpeta temporal
        temp_dir = os.path.join(extract_to, "temp_extraction")
        zip_ref.extractall(temp_dir)

        # Obtenir el nom de la carpeta principal (per exemple, "Dinamic-apk-main")
        extracted_folders = os.listdir(temp_dir)
        if len(extracted_folders) == 1:
            # Si només hi ha una carpeta, moure el seu contingut
            version_folder = os.path.join(temp_dir, extracted_folders[0])
            for item in os.listdir(version_folder):
                source = os.path.join(version_folder, item)
                destination = os.path.join(extract_to, item)

                # Ignorar les carpetes "actualizador" i "mysql"
                if 'actualizador' in item or 'mysql' in item:
                    continue

                # Moure el contingut
                if os.path.isdir(source ):
                    shutil.move(source, destination)
                else:
                    shutil.move(source, destination)

                # Si es troba un fitxer version.txt, moure'l a la carpeta de destí
                if item == "version.txt":
                    try:
                        shutil.move(source, VERSION_FILE)
                    except FileNotFoundError:
                        print(f"El fitxer {source} no es va trobar per moure'l a {VERSION_FILE}")

        else:
            # Si hi ha múltiples carpetes, moure cada fitxer o carpeta a la carpeta de destí
            for item in extracted_folders:
                source = os.path.join(temp_dir, item)
                destination = os.path.join(extract_to, item)

                # Ignorar les carpetes "actualizador" i "mysql"
                if 'actualizador' in item or 'mysql' in item:
                    continue

                # Moure el contingut
                if os.path.isdir(source):
                    shutil.move(source, destination)
                else:
                    shutil.move(source, destination)

                # Si es troba un fitxer version.txt, moure'l a la carpeta de destí
                if item == "version.txt":
                    try:
                        shutil.move(source, VERSION_FILE)
                    except FileNotFoundError:
                        print(f"El fitxer {source} no es va trobar per moure'l a {VERSION_FILE}")

# Funció per actualitzar en un fil separat
def update():
    threading.Thread(target=perform_update).start()

def perform_update():
    close_other_python_processes()  # Tancar altres processos de Python
    clear_destination_folder()  # Netejar la carpeta de destí
    current_version = get_current_version()
    latest_version = "1.0.1"  # Aquí hauries d'implementar la lògica per obtenir l'última versió

    if current_version != latest_version:
        try:
            zip_path = os.path.join(UPDATER_FOLDER, "update.zip")
            download_file(ZIP_URL, zip_path)  # Descarregar el fitxer ZIP
            extract_zip(zip_path, DESTINATION_FOLDER)  # Extreure el fitxer ZIP
            messagebox.showinfo("Actualització", "L'actualització s'ha completat amb èxit.")
        except Exception as e:
            messagebox.showerror("Error", f"S'ha produït un error durant l'actualització: {e}")
    else:
        messagebox.showinfo("Actualització", "Ja tens l'última versió.")

# Codi per iniciar l'aplicació
root = tk.Tk()
root.title("Actualitzador Dinamic")
progress_bar = ttk.Progressbar(root, length=300)
progress_bar.pack(pady=20)

# Botó per iniciar l'actualització
update_button = ttk.Button(root, text="Actualitzar", command=update)
update_button.pack(pady=10)

root.mainloop()