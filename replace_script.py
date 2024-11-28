import os
import zipfile
import urllib.request
import shutil
import sys
from pathlib import Path
import winshell
import ctypes

# Ruta donde se descargará el archivo ZIP
url = 'https://github.com/aemon1977/Dinamic-apk/archive/refs/heads/main.zip'
download_path = r'C:\Dynamic\main.zip'
extract_folder = r'C:\Dynamic\Dinamic'
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
        zip_ref.extractall(extract_folder)
    print("Descompresión completada.")

# Función para crear un acceso directo
def create_shortcut():
    print("Creando acceso directo en el escritorio...")
    shortcut_path = os.path.join(winshell.desktop(), 'app_es.lnk')
    target = app_file
    w_dir = os.path.dirname(target)
    icon = target
    with winshell.shortcut(shortcut_path) as link:
        link.path = target
        link.working_directory = w_dir
        link.icon_location = icon
    print("Acceso directo creado.")

# Función para sustituirse a sí mismo
def replace_script():
    print("Sustituyendo script...")
    script_path = os.path.abspath(sys.argv[0])
    destination = os.path.join(extract_folder, 'Dinamic-apk-main', 'replace_script.py')

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
