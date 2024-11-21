import tkinter as tk
from tkinter import ttk, messagebox
import mysql.connector
import pandas as pd
import os

# Configuración de la conexión a la base de datos
config = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'database': 'gimnas'
}

# Función para cargar actividades de la base de datos
def cargar_actividades():
    actividades = []
    try:
        conn = mysql.connector.connect(**config)
        cursor = conn.cursor()
        cursor.execute("SELECT nom FROM activitats")
        actividades = [row[0] for row in cursor.fetchall()]
        conn.close()
    except mysql.connector.Error as e:
        messagebox.showerror("Error", f"Error al conectar a la base de datos: {e}")
    return actividades

# Función para cargar socios según la actividad seleccionada
def cargar_socios(actividad):
    socios = []
    try:
        conn = mysql.connector.connect(**config)
        cursor = conn.cursor()
        cursor.execute("SELECT Nom FROM socis WHERE FIND_IN_SET(%s, Activitats) ORDER BY Nom ASC", (actividad,))
        socios = [row[0] for row in cursor.fetchall()]
        conn.close()
    except mysql.connector.Error as e:
        messagebox.showerror("Error", f"Error al conectar a la base de datos: {e}")
    return socios

# Función para generar el archivo Excel
def generar_excel(socios, actividad):
    if not socios:
        messagebox.showwarning("Advertencia", "No hay socios para esta actividad.")
        return

    # Crear el archivo Excel
    data = []
    for socio in socios:
        data.append([socio])  # Cada socio en una fila

    df = pd.DataFrame(data, columns=["Socio"])
    excel_filename = f"socis_activitat_{actividad}.xlsx"
    df.to_excel(excel_filename, index=False, engine='openpyxl')

    # Abrir el archivo Excel automáticamente
    try:
        os.startfile(excel_filename)  # Para Windows
    except AttributeError:
        os.system(f"open {excel_filename}")  # Para macOS
        os.system(f"xdg-open {excel_filename}")  # Para Linux

    messagebox.showinfo("Éxito", f"Excel generado: {excel_filename}")

# Función para mostrar los socios en la interfaz
def mostrar_socios():
    actividad = combo_actividades.get()
    if not actividad:
        messagebox.showwarning("Advertencia", "Por favor, selecciona una actividad.")
        return

    socios = cargar_socios(actividad)
    if socios:
        # Limpiar la lista antes de agregar los nuevos socios
        listbox_socios.delete(0, tk.END)

        # Añadir los socios al Listbox
        for socio in socios:
            listbox_socios.insert(tk.END, socio)

        # Habilitar el botón para generar el Excel
        btn_generar_excel.config(state=tk.NORMAL)
    else:
        listbox_socios.delete(0, tk.END)
        messagebox.showinfo("Información", "No hay socios para esta actividad.")

# Función para filtrar los socios según el texto de búsqueda
def buscar_socio():
    query = entry_busqueda.get().lower()  # Obtener el texto de búsqueda en minúsculas
    actividad = combo_actividades.get()

    if not actividad:
        messagebox.showwarning("Advertencia", "Por favor, selecciona una actividad.")
        return

    socios = cargar_socios(actividad)
    socios_filtrados = [socio for socio in socios if query in socio.lower()]

    # Limpiar la lista antes de agregar los socios filtrados
    listbox_socios.delete(0, tk.END)

    # Añadir los socios filtrados al Listbox
    for socio in socios_filtrados:
        listbox_socios.insert(tk.END, socio)

# Interfaz gráfica
root = tk.Tk()
root.title("Selecciona Activitat")
root.geometry("400x450")

label = tk.Label(root, text="Selecciona Activitat")
label.pack(pady=10)

# Cargar actividades en un ComboBox
combo_actividades = ttk.Combobox(root, values=cargar_actividades(), state="readonly")
combo_actividades.pack(pady=5)
combo_actividades.set("Selecciona una activitat")

btn_cargar_socios = tk.Button(root, text="Mostra Socis", command=mostrar_socios)
btn_cargar_socios.pack(pady=10)

# Campo de búsqueda
entry_busqueda = tk.Entry(root, width=30)
entry_busqueda.pack(pady=5)
btn_buscar = tk.Button(root, text="Buscar Soci", command=buscar_socio)
btn_buscar.pack(pady=5)

# Listbox para mostrar los socios
listbox_socios = tk.Listbox(root, width=40, height=10)
listbox_socios.pack(pady=10)

# Botón para generar el archivo Excel
btn_generar_excel = tk.Button(root, text="Generar Excel", command=lambda: generar_excel(cargar_socios(combo_actividades.get()), combo_actividades.get()), state=tk.DISABLED)
btn_generar_excel.pack(pady=10)

root.mainloop()
