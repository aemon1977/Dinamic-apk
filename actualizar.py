import os
import zipfile
import urllib.request
import shutil
import sys
import winshell

# Ruta donde se descargará el archivo ZIP
url = 'https://github.com/aemon1977/Dinamic-apk/archive/refs/heads/main.zip'
download_path = r'C:\Dinamic\main.zip'
extract_folder = r'C:\Dinamic'
app_file = os.path.join(extract_folder, 'Dinamic-apk-main', 'app.es')

# Función para descargar el archivo ZIP
def download_zip():
    print("Descargando archivo ZIP...")
    urllib.request.urlretrieve(url, download_path)
    print("Archivo descargado.")

# Función para descomprimir el archivo ZIP
def unzip_file():
    print("Descomprimiendo archivo ZIP...")
    with zipfile.ZipFile(download_path, 'r') as zip_ref:
        # Extraemos el contenido directamente en C:\Dinamic
        zip_ref.extractall(extract_folder)
    print("Descompresión completada.")

# Función para mover los archivos de la subcarpeta a la carpeta principal
def move_files():
    print("Moviendo archivos a C:\\Dinamic...")
    extracted_folder = os.path.join(extract_folder, 'Dinamic-apk-main')

    # Mover todos los archivos de la subcarpeta a la carpeta principal
    for item in os.listdir(extracted_folder):
        s = os.path.join(extracted_folder, item)
        d = os.path.join(extract_folder, item)
        if os.path.isdir(s):
            shutil.move(s, d)
        else:
            shutil.move(s, d)
    print("Archivos movidos.")

# Función para eliminar la subcarpeta vacía
def remove_subfolder():
    extracted_folder = os.path.join(extract_folder, 'Dinamic-apk-main')
    if os.path.exists(extracted_folder):
        shutil.rmtree(extracted_folder)
        print("Subcarpeta eliminada.")

# Función para crear un acceso directo
def create_shortcut():
    print("Creando acceso directo en el escritorio...")
    shortcut_path = os.path.join(winshell.desktop(), 'app_es.lnk')
    target = app_file
    w_dir = os.path.dirname(target)
    icon = target  # Usamos el mismo archivo como ícono
    icon_index = 0  # Usamos el primer ícono del archivo

    # Crear acceso directo
    with winshell.shortcut(shortcut_path) as link:
        link.path = target
        link.working_directory = w_dir
        link.icon_location = (icon, icon_index)  # Pasamos una tupla (ruta, índice)
    print("Acceso directo creado.")

# Función para sustituirse a sí mismo
def replace_script():
    print("Sustituyendo script...")
    script_path = os.path.abspath(sys.argv[0])
    destination = os.path.join(extract_folder, 'replace_script.py')

    if os.path.exists(destination):
        os.remove(destination)
    shutil.copy(script_path, destination)
    print("Script sustituido.")

# Función principal que ejecuta todo el proceso
def main():
    # Crear la carpeta de destino si no existe
    if not os.path.exists(extract_folder):
        os.makedirs(extract_folder)

    # Descargar y descomprimir el archivo
    download_zip()
    unzip_file()

    # Mover los archivos de la subcarpeta a la carpeta principal
    move_files()

    # Eliminar la subcarpeta vacía
    remove_subfolder()

    # Crear acceso directo
    create_shortcut()

    # Sustituir el script
    replace_script()

    # Eliminar archivo ZIP después de la instalación
    if os.path.exists(download_path):
        os.remove(download_path)
    print("Proceso completado.")

if __name__ == '__main__':
    main()
