# modificar1.py

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import mysql.connector
from PIL import Image, ImageTk
import io
import configparser

# Leer la configuración de la base de datos desde config.ini
config = configparser.ConfigParser()
config.read('config.ini')

# Configuración de la base de datos
def conectar_db():
    return mysql.connector.connect(
        host=config['mysql']['host'],
        user=config['mysql']['user'],
        password=config['mysql']['password'],
        database=config['mysql']['database']
    )

# Variables y campos del formulario
foto_ruta = None

# Función para cargar datos en el formulario
def cargar_en_formulario(event):
    selected_item = event.widget.selection()
    if selected_item:
        item = event.widget.item(selected_item)
        datos = item['values']
        
        entrada_dni.delete(0, tk.END)
        entrada_dni.insert(0, datos[1])
        # Completar con el resto de campos del formulario...

# Función para guardar cambios
def guardar_cambios():
    # Implementación de guardar cambios en la base de datos
    pass

# Función para cargar actividades
def cargar_activitats_disponibles():
    # Implementación para cargar actividades desde la base de datos
    pass

# Configuración de la interfaz gráfica para el formulario
root = tk.Tk()
root.title("Modificar Socis")

# Frame para el formulario
frame_formulario = tk.Frame(root)
frame_formulario.pack(pady=40)

# Campos del formulario
tk.Label(frame_formulario, text="DNI").grid(row=0, column=0)
entrada_dni = tk.Entry(frame_formulario, width=35)
entrada_dni.grid(row=0, column=1)

# Completar el resto de campos del formulario...

# Botón para guardar cambios
btn_guardar = tk.Button(root, text="Desa", command=guardar_cambios)
btn_guardar.pack(pady=20)

root.mainloop()
