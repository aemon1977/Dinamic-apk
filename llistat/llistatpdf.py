import tkinter as tk
from tkinter import ttk, messagebox
import mysql.connector
from mysql.connector import Error
from fpdf import FPDF
import os
import configparser

# Leer configuración desde config.ini
config = configparser.ConfigParser()
config.read("config.ini")

db_config = {
    'host': config['mysql']['host'],
    'user': config['mysql']['user'],
    'password': config['mysql']['password'],
    'database': config['mysql']['database']
}

# Función para cargar actividades de la base de datos
def cargar_actividades():
    actividades = []
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        cursor.execute("SELECT nom FROM activitats")
        actividades = [row[0] for row in cursor.fetchall()]
        conn.close()
    except Error as e:
        messagebox.showerror("Error", f"Error al conectar a la base de datos: {e}")
    return actividades

# Función para generar el PDF con los socios de la actividad seleccionada
def generar_pdf():
    actividad = combo_actividades.get()
    if not actividad or actividad == "Selecciona una activitat":
        messagebox.showwarning("Advertencia", "Por favor, selecciona una actividad.")
        return

    socios = []
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        cursor.execute("SELECT Nom FROM socis WHERE FIND_IN_SET(%s, Activitats) ORDER BY Nom ASC", (actividad,))
        socios = [row[0] for row in cursor.fetchall()]
        conn.close()
    except Error as e:
        messagebox.showerror("Error", f"Error al conectar a la base de datos: {e}")
        return

    if socios:
        pdf_filename = f"socis_activitat_{actividad}.pdf"
        pdf = FPDF()
        pdf.set_auto_page_break(auto=True, margin=15)

        # Parámetros de la cuadrícula
        cell_height = 6  
        first_cell_width = 70  
        subsequent_cell_width = 5  
        margin = 10  
        total_columns = 25  
        y_position = 40  
        total_rows = 40  

        pdf.add_page()
        pdf.set_font("Arial", "B", 16)
        pdf.cell(0, 10, actividad, 0, 1, "C")
        pdf.set_font("Arial", "", 12)
        pdf.ln(10)

        for row_index in range(total_rows):
            pdf.rect(margin, y_position + row_index * cell_height, first_cell_width + 5, cell_height)

            for col in range(1, total_columns):
                pdf.rect(margin + first_cell_width + (col - 1) * subsequent_cell_width, y_position + row_index * cell_height, subsequent_cell_width, cell_height)

            if row_index < len(socios):
                pdf.set_xy(margin + 1, y_position + row_index * cell_height + 1)
                pdf.cell(first_cell_width + 5, cell_height, socios[row_index])

        for row_index in range(total_rows, len(socios)):
            if row_index % total_rows == 0:
                pdf.add_page()
                y_position = 40  

            pdf.rect(margin, y_position + (row_index % total_rows) * cell_height, first_cell_width, cell_height)

            for col in range(1, total_columns):
                pdf.rect(margin + first_cell_width + (col - 1) * subsequent_cell_width, y_position + (row_index % total_rows) * cell_height, subsequent_cell_width, cell_height)

            pdf.set_xy(margin + 1, y_position + (row_index % total_rows) * cell_height + 1)
            pdf.cell(first_cell_width, cell_height, socios[row_index])

        pdf.output(pdf_filename)

        # Abrir el PDF automáticamente
        try:
            os.startfile(pdf_filename)  
        except AttributeError:
            os.system(f"open {pdf_filename}")  
            os.system(f"xdg-open {pdf_filename}")  

    else:
        messagebox.showinfo("Información", "No se encontraron socios para esta actividad.")

# Interfaz gráfica
root = tk.Tk()
root.title("Seleccionar Activitat")
root.geometry("400x200")

label = tk.Label(root, text="Seleccionar Activitat")
label.pack(pady=10)

combo_actividades = ttk.Combobox(root, values=cargar_actividades(), state="readonly")
combo_actividades.pack(pady=5)
combo_actividades.set("Selecciona una activitat")

btn_generar = tk.Button(root, text="Buscar y Generar PDF", command=generar_pdf)
btn_generar.pack(pady=20)

root.mainloop()
