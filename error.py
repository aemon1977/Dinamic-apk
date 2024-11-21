import sys
import subprocess
import os
import logging
import importlib.util

# Función para instalar módulos si no están instalados
def instalar_modulo(modulo):
    try:
        # Intentar importar el módulo
        importlib.import_module(modulo)
    except ImportError:
        # Si no está instalado, intentar instalarlo
        logging.info(f"El módulo '{modulo}' no está instalado. Instalando...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", modulo])

# Configurar el archivo de log
log_file = "verificacion_python_interferencias.log"
logging.basicConfig(filename=log_file, level=logging.DEBUG, 
                    format='%(asctime)s - %(levelname)s - %(message)s')

# Lista de módulos necesarios
modulos_necesarios = ['psutil']

# Instalar módulos necesarios
for modulo in modulos_necesarios:
    instalar_modulo(modulo)

# Importar psutil después de asegurarse de que esté instalado
import psutil

# Lista de aplicaciones conocidas que pueden interferir
interferencias_posibles = [
    'antivirus',          # Ejemplo: nombre genérico del antivirus
    'vmware',             # Ejemplo: VMware
    'virtualbox',         # Ejemplo: VirtualBox
    'onedrive',           # Ejemplo: OneDrive
    'dropbox',            # Ejemplo: Dropbox
    'ccleaner',           # Ejemplo: CCleaner
    'revo',               # Ejemplo: Revo Uninstaller
]

def verificar_python():
    try:
        # Verificar si Python está instalado
        python_version = subprocess.check_output([sys.executable, '--version'], stderr=subprocess.STDOUT).decode('utf-8').strip()
        logging.info(f"Python encontrado: {python_version}")
        print(f"Python encontrado: {python_version}")

        # Verificar si se pueden ejecutar aplicaciones Python (intenta ejecutar un script simple)
        test_script = 'test_script.py'
        with open(test_script, 'w') as f:
            f.write('print("Hola desde el script de prueba")')

        # Ejecutar el script de prueba
        subprocess.run([sys.executable, test_script], check=True)
        logging.info("Aplicación Python ejecutada con éxito.")
        print("Aplicación Python ejecutada con éxito.")

        # Eliminar el script de prueba
        os.remove(test_script)

    except subprocess.CalledProcessError as e:
        logging.error(f"Error al ejecutar el script de prueba: {e}")
        print(f"Error al ejecutar el script de prueba. Consulte el archivo de log '{log_file}' para más detalles.")
    except FileNotFoundError:
        logging.error("Python no está instalado o no se puede encontrar el ejecutable.")
        print("Python no está instalado o no se puede encontrar el ejecutable. Consulte el archivo de log para más detalles.")
    except Exception as e:
        logging.error(f"Ocurrió un error inesperado: {e}")
        print(f"Ocurrió un error inesperado. Consulte el archivo de log '{log_file}' para más detalles.")

def verificar_interferencias():
    try:
        # Obtener todos los procesos en ejecución
        procesos = [p.info['name'].lower() for p in psutil.process_iter(attrs=['name'])]
        
        # Verificar si alguna de las aplicaciones problemáticas está corriendo
        interferencias = [app for app in interferencias_posibles if app in procesos]
        
        if interferencias:
            logging.warning(f"Posibles interferencias encontradas: {', '.join(interferencias)}")
            print(f"Advertencia: Posibles interferencias encontradas: {', '.join(interferencias)}")
        else:
            logging.info("No se encontraron interferencias conocidas.")
            print("No se encontraron interferencias conocidas.")
    
    except Exception as e:
        logging.error(f"Error al verificar interferencias: {e}")
        print(f"Error al verificar interferencias. Consulte el archivo de log para más detalles.")

if __name__ == "__main__":
    # Verificar Python
    verificar_python()
    
    # Verificar interferencias con otras aplicaciones
    verificar_interferencias()
