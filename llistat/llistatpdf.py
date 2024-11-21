import tkinter as tk
from tkinter import ttk, messagebox
import mysql.connector
from fpdf import FPDF
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

# Función para generar el PDF con los socios de la actividad seleccionada
def generar_pdf():
    actividad = combo_actividades.get()
    if not actividad:
        messagebox.showwarning("Advertencia", "Por favor, selecciona una actividad.")
        return

    socios = []
    try:
        conn = mysql.connector.connect(**config)
        cursor = conn.cursor()
        cursor.execute("SELECT Nom FROM socis WHERE FIND_IN_SET(%s, Activitats) ORDER BY Nom ASC", (actividad,))
        socios = [row[0] for row in cursor.fetchall()]
        conn.close()
    except mysql.connector.Error as e:
        messagebox.showerror("Error", f"Error al conectar a la base de datos: {e}")
        return

    if socios:
        pdf_filename = f"socis_activitat_{actividad}.pdf"
        pdf = FPDF()
        pdf.set_auto_page_break(auto=True, margin=15)  # Activar salto automático de página

        # Parametros de la cuadrícula
        cell_height = 6  # Altura de la celda (0.6 cm)
        first_cell_width = 70  # Ancho de la primera celda (5 cm)
        subsequent_cell_width = 5  # Ancho de las celdas siguientes (0.5 cm)
        margin = 10  # Margen de la página
        total_columns = 25  # Total de columnas (1 celda ancha + 24 celdas estrechas)
        y_position = 40  # Posición inicial de las filas
        total_rows = 40  # Total de filas a rellenar por página

        # Primer página con 5cm más de ancho para la primera celda
        pdf.add_page()
        pdf.set_font("Arial", "B", 16)
        pdf.cell(0, 10, actividad, 0, 1, "C")
        pdf.set_font("Arial", "", 12)
        pdf.ln(10)

        # Dibujar la cuadrícula completa en la primera página
        for row_index in range(total_rows):
            # Dibujar la primera celda con ancho diferente
            pdf.rect(margin, y_position + row_index * cell_height, first_cell_width + 5, cell_height)

            # Dibujar las celdas siguientes sin espacio entre ellas
            for col in range(1, total_columns):
                pdf.rect(margin + first_cell_width + (col - 1) * subsequent_cell_width, y_position + row_index * cell_height, subsequent_cell_width, cell_height)

            # Si hay nombres de socios, insertarlos en la primera celda
            if row_index < len(socios):
                pdf.set_xy(margin + 1, y_position + row_index * cell_height + 1)  # Ajustamos la posición vertical
                pdf.cell(first_cell_width + 5, cell_height, socios[row_index])

        # Continuar añadiendo más páginas si es necesario
        for row_index in range(total_rows, len(socios)):
            if row_index % total_rows == 0:
                pdf.add_page()
                y_position = 40  # Restablecer la posición inicial en la nueva página

            # Dibujar la primera celda con ancho diferente
            pdf.rect(margin, y_position + (row_index % total_rows) * cell_height, first_cell_width, cell_height)

            # Dibujar las celdas siguientes sin espacio entre ellas
            for col in range(1, total_columns):
                pdf.rect(margin + first_cell_width + (col - 1) * subsequent_cell_width, y_position + (row_index % total_rows) * cell_height, subsequent_cell_width, cell_height)

            # Insertar el nombre del socio
            pdf.set_xy(margin + 1, y_position + (row_index % total_rows) * cell_height + 1)  # Ajustar posición
            pdf.cell(first_cell_width, cell_height, socios[row_index])

        pdf.output(pdf_filename)

        # Abrir el documento PDF automáticamente
        try:
            os.startfile(pdf_filename)  # Para Windows
        except AttributeError:
            os.system(f"open {pdf_filename}")  # Para macOS
            os.system(f"xdg-open {pdf_filename}")  # Para Linux

    
    else:
        messagebox.showinfo("Información", "No se encontraron socios para esta actividad.")

# Interfaz gráfica
root = tk.Tk()
root.title("Seleccionar Activitat")
root.geometry("400x200")

label = tk.Label(root, text="Seleccionar Activitat")
label.pack(pady=10)

# Cargar actividades en un ComboBox
combo_actividades = ttk.Combobox(root, values=cargar_actividades(), state="readonly")
combo_actividades.pack(pady=5)
combo_actividades.set("Selecciona una activitat")

btn_generar = tk.Button(root, text="Buscar y Generar PDF", command=generar_pdf)
btn_generar.pack(pady=20)

root.mainloop()
