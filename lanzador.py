import importlib
import sys
import subprocess
import traceback
import logging

# Configurar el archivo de registro
logging.basicConfig(
    filename='registro_dinamic.log',
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Registrar los módulos importados
def registrar_modulos():
    logging.info('Módulos utilizados en dinamic.py:')
    for name in sorted(sys.modules.keys()):
        try:
            module = importlib.import_module(name)
            if module:
                logging.info(f'Módulo: {name}')
        except ImportError:
            pass

# Ejecutar el script principal y capturar errores
def launch_dinamic():
    try:
        logging.info('Iniciando la ejecución de dinamic.py')
        registrar_modulos()
        # Ejecuta el script de Python sin configuraciones adicionales
        subprocess.run(['python', 'dinamic.py'], check=True)
    except subprocess.CalledProcessError as e:
        logging.error('Error al ejecutar dinamic.py')
        logging.error(str(e))
        print(f"Error al ejecutar dinamic.py: {e}")
    except FileNotFoundError:
        logging.error('Archivo dinamic.py no encontrado.')
        print("Archivo dinamic.py no encontrado.")
    except Exception as e:
        logging.error('Error inesperado durante la ejecución de dinamic.py')
        logging.error(traceback.format_exc())
        print(f'Se ha producido un error. Revisa el archivo registro_dinamic.log para más detalles.')

if __name__ == "__main__":
    launch_dinamic()
