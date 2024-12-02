import traceback
import logging
import subprocess
import importlib
import sys
import os

# Configurar el archivo de registro
logging.basicConfig(
    filename='registro_dinamic.log',
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Registrar los módulos importados
def registrar_modulos():
    logging.info('Módulos utilizados en gimnas.py:')
    for name in sorted(sys.modules.keys()):
        try:
            module = importlib.import_module(name)
            if module:
                logging.info(f'Módulo: {name}')
        except ImportError:
            pass

# Función para lanzar mysqld.exe
def launch_mysql_server():
    mysql_path = r'c:\dinamic\mysql\bin\mysqld.exe'
    try:
        if not os.path.exists(mysql_path):
            logging.error(f'No se encontró el ejecutable en {mysql_path}')
            print(f"No se encontró el ejecutable en {mysql_path}")
            return
        logging.info('Iniciando MySQL Server...')
        subprocess.Popen(
            [mysql_path],
            creationflags=subprocess.CREATE_NO_WINDOW,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        logging.info('MySQL Server iniciado correctamente.')
    except Exception as e:
        logging.error('Error al iniciar MySQL Server.')
        logging.error(traceback.format_exc())
        print(f'Error al iniciar MySQL Server. Revisa el archivo registro_dinamic.log para más detalles.')

# Ejecutar el script principal y capturar errores
def launch_dinamic():
    try:
        logging.info('Iniciando la ejecución de gimnas.py')
        registrar_modulos()
        # Ejecuta el script de Python sin mostrar la ventana de terminal
        subprocess.run(['python', 'gimnas.py'], check=True, creationflags=subprocess.CREATE_NO_WINDOW)
    except subprocess.CalledProcessError as e:
        logging.error('Error al ejecutar gimnas.py')
        logging.error(str(e))
        print(f"Error al ejecutar gimnas.py: {e}")
    except FileNotFoundError:
        logging.error('Archivo gimnas.py no encontrado.')
        print("Archivo gimnas.py no encontrado.")
    except Exception as e:
        logging.error('Error inesperado durante la ejecución de gimnas.py')
        logging.error(traceback.format_exc())
        print(f'Se ha producido un error. Revisa el archivo registro_dinamic.log para más detalles.')

if __name__ == "__main__":
    # Lanzar el servidor MySQL
    launch_mysql_server()
    # Lanzar gimnas.py
    launch_dinamic()
