import os
import tkinter as tk
from tkinter import messagebox
import mysql.connector
from mysql.connector import Error
from tkinter import ttk
from PIL import Image, ImageTk
import subprocess
import requests
import logging
import threading

# Configuración del logger
logging.basicConfig(
    filename="app_error.log",  # Nombre del archivo donde se guardarán los logs
    level=logging.ERROR,  # Nivel de logs (ERROR para capturar solo errores)
    format="%(asctime)s - %(levelname)s - %(message)s"  # Formato del log
)

# Archivo para almacenar la fecha de la última verificación
LAST_CHECK_FILE = "last_check.txt"
VERSION_FILE = "version.txt"  # Archivo que contiene la versión actual

# Función para leer la versión actual desde un archivo
def read_current_version():
    try:
        with open(VERSION_FILE, 'r') as file:
            return file.read().strip()
    except FileNotFoundError:
        return "0.0.0"  # Valor por defecto si no se encuentra el archivo

# Función para verificar actualizaciones
def check_for_updates():
    current_version = read_current_version()  # Leer la versión desde el archivo
    try:
        response = requests.get("https://api.github.com/repos/aemon1977/Dinamic-apk/releases/latest")
        response.raise_for_status()  # Lanza un error si la solicitud falla
        latest_release = response.json()
        latest_version = latest_release['tag_name'].lstrip('v')  # Eliminar el prefijo 'v' si existe
        
        if latest_version != current_version:
            show_update_notification(latest_version, latest_release['html_url'])
        else:
            print("Estás utilizando la última versión.")
    except requests.RequestException as e:
        print(f"Error al acceder a la API de GitHub: {e}")

def show_update_notification(latest_version, release_url):
    message = f"Hi ha disponible una nova versió"
    messagebox.showinfo("Actualizació Disponible", message)

# Llama a la función al inicio de tu aplicación
check_for_updates()

# Configure logging
logging.basicConfig(filename='mysql_shutdown.log', level=logging.DEBUG, format='%(asctime)s:%(levelname)s:%(message)s')

def tancar_servici_mysql():
    try:
        # Absolute path to mysqladmin
        mysqladmin_path = r"\Dinamic\mysql\bin\mysqladmin.exe"
        
        # Command to shut down MySQL service
        command = [mysqladmin_path, '-u', 'root', 'shutdown']
        
        # Execute the command
        result = subprocess.run(command, capture_output=True, text=True)
        
        # Log the output
        if result.returncode == 0:
            logging.info("MySQL service shut down successfully.")
        else:
            logging.error(f"Failed to shut down MySQL service: {result.stderr}")
    except Exception as e:
        logging.error(f"Error shutting down MySQL service: {str(e)}")

def sortir():
    if messagebox.askokcancel("Sortir", "Vols sortir de l'aplicació?"):
        tancar_servici_mysql()  # Shut down the MySQL service
        root.destroy()  # Close the GUI window

def al_tancar():
    sortir()  # Call the sortir function when the window is closed

# Configuración del logger
logging.basicConfig(
    filename="app_error.log",  # Nombre del archivo donde se guardarán los logs
    level=logging.ERROR,  # Nivel de logs (ERROR para capturar solo errores)
    format="%(asctime)s - %(levelname)s - %(message)s"  # Formato del log
)

# Función para conectarse a la base de datos y obtener datos
def get_data():
    connection = None
    try:
        connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password='',  # Cambia esto si es diferente
            database='gimnas'
        )
        if connection.is_connected():
            cursor = connection.cursor(dictionary=True)

            # Obtener esporádicos
            cursor.execute("""
                SELECT Nom, Telefon1,  DATEDIFF(Baixa, CURDATE()) AS Dies_Fins_Baixa
                FROM esporadics
                WHERE Baixa >= CURDATE()
                ORDER BY Dies_Fins_Baixa ASC
                LIMIT 10
            """)
            esporadics = cursor.fetchall()

            # Obtener próximos cumpleaños
            cursor.execute("""
                SELECT Nom, Telefon1, Activitats,
                    DATEDIFF(
                        IF(
                            DATE(CONCAT(YEAR(CURDATE()), '-', MONTH(Data_naixement), '-', DAY(Data_naixement))) >= CURDATE(),
                            DATE(CONCAT(YEAR(CURDATE()), '-', MONTH(Data_naixement), '-', DAY(Data_naixement))),
                            DATE(CONCAT(YEAR(CURDATE() + INTERVAL 1 YEAR), '-', MONTH(Data_naixement), '-', DAY(Data_naixement)))
                        ),
                        CURDATE()
                    ) AS Dies_Fins_Aniversari
                FROM socis
                HAVING Dies_Fins_Aniversari >= 0
                ORDER BY Dies_Fins_Aniversari ASC
            """)
            birthdays = cursor.fetchall()

            # Consultar totales
            cursor.execute("SELECT COUNT(*) AS total FROM socis")
            total_socis = cursor.fetchone()['total']

            cursor.execute("SELECT COUNT(*) AS actius FROM socis WHERE Activitats != ''")
            socis_actius = cursor.fetchone()['actius']

            cursor.execute("SELECT SUM(Quantitat) AS totalQuantitat FROM socis WHERE Activitats != ''")
            total_quantitat_socis = cursor.fetchone()['totalQuantitat'] or 0

            cursor.execute("SELECT SUM(Quantitat) AS totalQuantitat FROM esporadics WHERE Baixa >= CURDATE() AND Quantitat IS NOT NULL")
            total_quantitat_esporadics = cursor.fetchone()['totalQuantitat'] or 0

            return esporadics, birthdays, total_socis, socis_actius, total_quantitat_socis, total_quantitat_esporadics

    except Error as e:
        messagebox.showerror("Error de Conexión", str(e))
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()

# Función para mostrar los datos en la interfaz
def display_data():
    esporadics, birthdays, total_socis, socis_actius, total_quantitat_socis, total_quantitat_esporadics = get_data()

    # Limpiar tablas
    for row in tree_esporadics.get_children():
        tree_esporadics.delete(row)
    for row in tree_birthdays.get_children():
        tree_birthdays.delete(row)

    # Llenar tabla de esporádicos
    for esporadic in esporadics:
        tree_esporadics.insert("", "end", values=(
            esporadic['Nom'], esporadic['Telefon1'], esporadic['Dies_Fins_Baixa']
        ))

    # Llenar tabla de cumpleaños
    for birthday in birthdays:
        tree_birthdays.insert("", "end", values=(
            birthday['Nom'], birthday['Telefon1'], birthday['Activitats'], birthday['Dies_Fins_Aniversari']
        ))

    # Mostrar totales
    label_totals.config(text=f"Total de Socis: {total_socis}\nSocis actius: {socis_actius}\nQuantitat Total (Socis): {total_quantitat_socis}\nQuantitat Total (Esporàdics): {total_quantitat_esporadics}")

# Función para abrir nuevas ventanas
def open_window(url):
    messagebox.showinfo("Información", f"Se abrirá: {url}")

# Función para ejecutar copia.py
def run_copia():
    subprocess.Popen(["python", os.path.join("copia.py")])  # Ejecutar copia.py

# Función para ejecutar restaura.py
def run_restaura():
    subprocess.Popen(["python", os.path.join("restaura.py")])  # Ejecutar restaura.py

# Función para ejecutar actualizar.py
def run_actualitza():
    # Crear un hilo para ejecutar el actualizador
    update_thread = threading.Thread(target=lambda: subprocess.Popen(["python", os.path.join("actualizador", "update.py")]))
    update_thread.start()  # Iniciar el hilo

# Función para ejecutar empresa.py
def run_empresa():
    subprocess.Popen(["python", os.path.join("empresa.py")])  # Ejecutar empresa.py

# Función para ejecutar activitats.py
def run_activitats():
    subprocess.Popen(["python", os.path.join("llistat", "activitats.py")])  # Ejecutar activitats.py

# Función para ejecutar llistatpdf.py
def run_llistatpdf():
    subprocess.Popen(["python", os.path.join("llistat", "llistatpdf.py")])  # Ejecutar llistatpdf.py

# Función para ejecutar llistat_excel.py
def run_llistat_excel():
    subprocess.Popen(["python", os.path.join("llistat", "llistat_excel.py")])  # Ejecutar llistat_excel.py

# Función para ejecutar insertar.py en la carpeta 'socis'
def run_insertar():
    subprocess.Popen(["python", os.path.join("socis", "insertar.py")])  # Ejecutar insertar.py

# Función para ejecutar filtro.py en la carpeta 'socis'
def run_modificar():
    subprocess.Popen(["python", os.path.join("socis", "filtro.py")])  # Ejecutar filtro.py

# Función para ejecutar fitxa.py en la carpeta 'socis'
def run_fitxa():
    subprocess.Popen(["python", os.path.join("socis", "fitxa.py")])  # Ejecutar fitxa.py

# Función para ejecutar llistatsocis.py en la carpeta 'socis'
def run_llistatsocis():
    subprocess.Popen(["python", os.path.join("socis", "llistatsocis.py")])  # Ejecutar fitxa.py

# Menus esporadics

# Función para ejecutar insertar.py en la carpeta 'esporadics'
def run_insertare():
    subprocess.Popen(["python", os.path.join("esporadics", "insertar.py")])  # Ejecutar insertar.py

# Función para ejecutar filtro.py en la carpeta 'esporadics'
def run_modificare():
    subprocess.Popen(["python", os.path.join("esporadics", "filtro.py")])  # Ejecutar filtro.py

# Función para ejecutar fitxa.py en la carpeta 'esporadics'
def run_fitxae():
    subprocess.Popen(["python", os.path.join("esporadics", "fitxa.py")])  # Ejecutar fitxa.py

# Función para ejecutar llistatsocis.py en la carpeta 'esporadics'
def run_llistatsocise():
    subprocess.Popen(["python", os.path.join("esporadics", "llistatsocis.py")])  # Ejecutar fitxa.py

# Función para ejecutar contabilitat.py en la carpeta 'comptabilitat'
def run_contabilitat():
    subprocess.Popen(["python", os.path.join("comptabilitat", "comptabilitatesporadics.py")])  # Ejecutar fitxa.py


# Configuración de la ventana principal
root = tk.Tk()
root.title("Gestió Gimnas")
root.geometry("800x600")  # Tamaño inicial de la ventana
root.minsize(800, 600)  # Tamaño mínimo de la ventana

# Configurar expansión para que la ventana se ajuste
root.grid_rowconfigure(1, weight=1)
root.grid_columnconfigure(0, weight=1)

# Set the protocol for window close
root.protocol("WM_DELETE_WINDOW", al_tancar)

# Barra de menú
menu_bar = tk.Menu(root)

# Menú de Activitats
Arxiu_menu = tk.Menu(menu_bar, tearoff=0)
Arxiu_menu.add_command(label="Copia de seguretat", command=run_copia)
Arxiu_menu.add_command(label="Restaura", command=run_restaura)
Arxiu_menu.add_command(label="Actualitza programa", command=run_actualitza)
Arxiu_menu.add_command(label="Empresa", command=run_empresa)
menu_bar.add_cascade(label="Arxiu", menu=Arxiu_menu)

# Menú de Activitats
activitats_menu = tk.Menu(menu_bar, tearoff=0)
activitats_menu.add_command(label="Afegir/Eliminar", command=run_activitats)
activitats_menu.add_command(label="Llistat PDF", command=run_llistatpdf)  # Ejecutar llistatpdf.py
activitats_menu.add_command(label="Llistat Excel", command=run_llistat_excel)  # Ejecutar llistat_excel.py
menu_bar.add_cascade(label="Activitats", menu=activitats_menu)

# Menú de Socis
socis_menu = tk.Menu(menu_bar, tearoff=0)
socis_menu.add_command(label="Afegir", command=run_insertar)  # Cambiado para ejecutar insertar.py
socis_menu.add_command(label="Modificar", command=run_modificar)  # Cambiado para ejecutar filtro.py
socis_menu.add_command(label="Fitxa", command=run_fitxa) # Cambiado para ejecutar fitxa.py
socis_menu.add_command(label="Llistat", command=run_llistatsocis) # Cambiado para ejecutar llistatsocis.py
menu_bar.add_cascade(label="Socis", menu=socis_menu)

# Menú de Esporádics
esporadics_menu = tk.Menu(menu_bar, tearoff=0)
esporadics_menu.add_command(label="Afegir", command=run_insertare)  # Cambiado para ejecutar insertar.py
esporadics_menu.add_command(label="Modificar", command=run_modificare)  # Cambiado para ejecutar filtro.py
esporadics_menu.add_command(label="Fitxa", command=run_fitxae) # Cambiado para ejecutar fitxa.py
esporadics_menu.add_command(label="Llistat", command=run_llistatsocise) # Cambiado para ejecutar llistatsocis.py
esporadics_menu.add_command(label="Contabilitat", command=run_contabilitat) # Cambiado para ejecutar contabilitat.py
menu_bar.add_cascade(label="Esporádics", menu=esporadics_menu)

# Menú de Comptabilitat
Comptabilitat_menu = tk.Menu(menu_bar, tearoff=0)
Comptabilitat_menu.add_command(label="Comptabilitat", command=run_contabilitat) # Cambiado para ejecutar contabilitat.py
menu_bar.add_cascade(label="Comptabilitat", menu=Comptabilitat_menu)

# Add "Sortir" menu item directly to the menu bar
menu_bar.add_command(label="Sortir", command=sortir)

# Configurar la barra de menú
root.config(menu=menu_bar)

# Logo
logo_path = os.path.join(os.path.dirname(__file__), 'logo', 'logo.jpg')
try:
    logo_image = Image.open(logo_path)
    logo_image = logo_image.resize((250, 100), Image.LANCZOS)  # Cambiado a LANCZOS
    logo_photo = ImageTk.PhotoImage(logo_image)
    logo_label = tk.Label(root, image=logo_photo)
    logo_label.grid(row=0, column=0, columnspan=3, pady=(10, 0), sticky='e')
except Exception as e:
    messagebox.showerror("Error al cargar el logo", str(e))

# Crear un marco para contener las tablas
frame = ttk.Frame(root)
frame.grid(row=1, column=0, padx=10, pady=10, sticky='nsew')

# Habilitar expansión de filas y columnas en el marco
frame.grid_rowconfigure(0, weight=0)  # Etiqueta de esporàdics no se expande
frame.grid_rowconfigure(1, weight=1)  # Tabla de esporàdics se expande
frame.grid_rowconfigure(2, weight=0)  # Etiqueta de cumpleaños no se expande
frame.grid_rowconfigure(3, weight=1)  # Tabla de cumpleaños se expande
frame.grid_columnconfigure(0, weight=1)

# Etiqueta para esporádicos
label_esporadics = tk.Label(frame, text="Esporàdics", font=("Arial", 14), fg="red")
label_esporadics.grid(row=0, column=0, sticky='w')

# Tabla de esporádicos
tree_esporadics = ttk.Treeview(frame, columns=("Nom", "Telefon1", "Dies_Fins_Baixa"), show='headings')
tree_esporadics.heading("Nom", text="Nom")
tree_esporadics.heading("Telefon1", text="Telefon 1")
tree_esporadics.heading("Dies_Fins_Baixa", text="Díes Fins Baixa")

# Agregar scrollbar a la tabla de esporádicos
scrollbar_esporadics = ttk.Scrollbar(frame, orient="vertical", command=tree_esporadics.yview)
tree_esporadics.configure(yscroll=scrollbar_esporadics.set)
scrollbar_esporadics.grid(row=1, column=1, sticky='ns')
tree_esporadics.grid(row=1, column=0, sticky='nsew')

# Etiqueta para cumpleaños
label_birthdays = tk.Label(frame, text="Proxims Aniversaris", font=("Arial", 14), fg="red")
label_birthdays.grid(row=2, column=0, sticky='w')

# Tabla de cumpleaños
tree_birthdays = ttk.Treeview(frame, columns=("Nom", "Telefon1", "Activitats", "Dies_Fins_Aniversari"), show='headings')
tree_birthdays.heading("Nom", text="Nom")
tree_birthdays.heading("Telefon1", text="Telefon 1")
tree_birthdays.heading("Activitats", text="Activitats")
tree_birthdays.heading("Dies_Fins_Aniversari", text="Dies Fins Aniversari")

# Agregar scrollbar a la tabla de cumpleaños
scrollbar_birthdays = ttk.Scrollbar(frame, orient="vertical", command=tree_birthdays.yview)
tree_birthdays.configure(yscroll=scrollbar_birthdays.set)
scrollbar_birthdays.grid(row=3, column=1, sticky='ns')
tree_birthdays.grid(row=3, column=0, sticky='nsew')

# Crear etiqueta para mostrar totales
label_totals = tk.Label(root, font=("Arial", 12), fg="red", justify="right")
label_totals.grid(row=2, column=0, padx=10, sticky='e')  # Alinear a la derecha

# Cargar datos al inicio
display_data()

# Iniciar el bucle principal
root.mainloop()
