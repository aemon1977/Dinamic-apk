import os
import zipfile
import urllib.request
import shutil
import sys
import winshell
import psutil
import subprocess
import ctypes

# Función para instalar módulos necesarios
def install(package):
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', package])

# Verificar e instalar módulos necesarios
def check_and_install_modules():
    try:
        import psutil
    except ImportError:
        print("psutil no está instalado. Instalando...")
        install('psutil')

    try:
        import winshell
    except ImportError:
        print("winshell no está instalado. Instalando...")
        install('winshell')

# Ruta donde se descargará el archivo ZIP
url = 'https://github.com/aemon1977/Dinamic-apk/archive/refs/heads/main.zip'
download_path = r'C:\Dinamic\main.zip'
extract_folder = r'C:\Dinamic'
app_exe = os.path.join(extract_folder, 'app.exe')  # Ruta de app.exe

# Función para descargar el archivo ZIP
def download_zip():
    print("Descargando archivo ZIP...")
    urllib.request.urlretrieve(url, download_path)
    print("Archivo descargado.")

# Función para descomprimir el archivo ZIP
def unzip_file():
    print("Descomprimiendo archivo ZIP...")
    with zipfile.ZipFile(download_path, 'r') as zip_ref:
        zip_ref.extractall(extract_folder)
    print("Descompresión completada.")

# Función para mover los archivos de la subcarpeta a la carpeta principal
def move_files():
    print("Moviendo archivos a C:\\Dinamic...")
    extracted_folder = os.path.join(extract_folder, 'Dinamic-apk-main')

    for item in os.listdir(extracted_folder):
        s = os.path.join(extracted_folder, item)
        d = os.path.join(extract_folder, item)

        if os.path.exists(d):
            if os.path.isdir(d):
                print(f"La carpeta {d} ya existe, se omite.")
            else:
                print(f"El archivo {d} ya existe, se omite.")
            continue

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
    shortcut_path = os.path.join(winshell.desktop(), 'Gimnas.lnk')
    target = app_exe
    w_dir = os.path.dirname(target)
    icon = target
    icon_index = 0

    with winshell.shortcut(shortcut_path) as link:
        link.path = target
        link.working_directory = w_dir
        link.icon_location = (icon, icon_index)
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

# Función para detener todos los procesos de Python excepto el propio
def stop_python_processes():
    current_pid = os.getpid()
    for proc in psutil.process_iter(['pid', 'name']):
        if proc.info['name'] == 'python.exe' and proc.info['pid'] != current_pid:
            try:
                proc.terminate()
                print(f"Proceso {proc.info['pid']} de Python detenido.")
            except psutil.NoSuchProcess:
                pass

# Función para mostrar una notificación al finalizar
def show_notification(message):
    try:
        ctypes.windll.user32.MessageBoxW(0, message, "Notificación", 0x40 | 0x1)
    except Exception as e:
        print(f"Error mostrando notificación: {e}")

# Función para lanzar app.exe
def launch_app():
    print("Lanzando app.exe...")
    
    if not os.path.exists(app_exe):
        print(f"Error: {app_exe} no encontrado.")
        return

    try:
        process = subprocess.Popen(app_exe, shell =True)
        print(f"app.exe lanzado correctamente (PID: {process.pid}).")
    except Exception as e:
        print(f"Error al lanzar app.exe: {e}")

# Función principal que ejecuta todo el proceso
def main():
    # Verificar e instalar módulos necesarios
    check_and_install_modules()

    # Detener procesos de Python (excepto el propio)
    stop_python_processes()

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
    
    # Mostrar notificación al finalizar
    show_notification("Proceso completado exitosamente.")

    # Lanzar app.exe
    launch_app()

if __name__ == '__main__':
    main()