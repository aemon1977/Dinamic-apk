import tkinter as tk
from tkinter import ttk, messagebox
import mysql.connector
from datetime import date
from configparser import ConfigParser
from fpdf import FPDF
import os
import subprocess

# Conexión a la base de datos
# Leer configuración desde config.ini
def leer_config():
    config = ConfigParser()
    config.read("config.ini")
    return config["mysql"]

# Conexión a la base de datos usando config.ini
def conectar_bd():
    config = leer_config()
    return mysql.connector.connect(
        host=config.get("host"),
        user=config.get("user"),
        password=config.get("password"),
        database=config.get("database")
    )

def buscar_clientes(event=None):  # Añadido el parámetro event
    criteri = entrada_busqueda.get()
    query = """
        SELECT ID, DNI, Nom, Activitats 
        FROM socis 
        WHERE Activitats IS NOT NULL AND (DNI LIKE %s OR Nom LIKE %s)
    """
    valors = (f"%{criteri}%", f"%{criteri}%")
    conexion = conectar_bd()
    cursor = conexion.cursor()
    cursor.execute(query, valors)
    resultats = cursor.fetchall()
    conexion.close()

    for row in tabla_busqueda.get_children():
        tabla_busqueda.delete(row)

    for resultat in resultats:
        tabla_busqueda.insert("", "end", values=resultat)

def passar_a_seleccio():
    for item in tabla_busqueda.selection():
        valors = tabla_busqueda.item(item, "values")
        if not any(valors[0] == seleccio.item(child, "values")[0] for child in seleccio.get_children()):
            seleccio.insert("", "end", values=valors)
        tabla_busqueda.delete(item)  # Eliminar de la taula de cerca

def treure_de_seleccio():
    for item in seleccio.selection():
        valors = seleccio.item(item, "values")
        tabla_busqueda.insert("", "end", values=valors)  # Retornar a la taula de cerca
        seleccio.delete(item)  # Eliminar de la taula de selecció

def realitzar_baixes():
    confirmacio = messagebox.askyesno("Confirmar", "Estàs segur de realitzar les baixes seleccionades?")
    if not confirmacio:
        return

    ids_seleccionats = [seleccio.item(item, "values")[0] for item in seleccio.get_children()]
    if not ids_seleccionats:
        messagebox.showwarning("Advertència", "No has seleccionat cap client.")
        return

    query = """
        UPDATE socis 
        SET Activitats = NULL, Baixa = %s 
        WHERE ID = %s
    """
    conexion = conectar_bd()
    cursor = conexion.cursor()
    data_avui = date.today().strftime("%Y-%m-%d")

    for id_client in ids_seleccionats:
        cursor.execute(query, (data_avui, id_client))

    conexion.commit()
    conexion.close()

    messagebox.showinfo("Èxit", "Les baixes s'han realitzat correctament.")
    buscar_clientes()
    for row in seleccio.get_children():
        seleccio.delete(row)

# Función para generar el PDF
def generar_pdf_baixes():
    if not seleccio.get_children():
        messagebox.showwarning("Advertència", "No hi ha cap client seleccionat per generar el PDF.")
        return

    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="Llista de Baixes", ln=True, align='C')

    pdf.set_font("Arial", size=10)
    pdf.cell(40, 10, txt="DNI", border=1, align='C')
    pdf.cell(60, 10, txt="Nom", border=1, align='C')
    pdf.cell(90, 10, txt="Activitats", border=1, ln=True, align='C')

    for item in seleccio.get_children():
        valors = seleccio.item(item, "values")
        pdf.cell(40, 10, txt=valors[1], border=1)
        pdf.cell(60, 10, txt=valors[2], border=1)
        pdf.cell(90, 10, txt=valors[3], border=1, ln=True)

    # Guardar el PDF
    pdf_path = "baixes.pdf"
    pdf.output(pdf_path)
    
    # Abrir el PDF automáticamente
    try:
        if os.name == 'nt':  # Windows
            os.startfile(pdf_path)
        elif os.name == 'posix':  # Linux o Mac
            subprocess.run(["xdg-open", pdf_path], check=True)
    except Exception as e:
        messagebox.showerror("Error", f"No s'ha pogut obrir el PDF: {e}")

# Funció per ordenar taula
def ordenar_taula(taula, columna):
    dades = [(taula.set(item, columna), item) for item in taula.get_children('')]
    dades_ordenades = sorted(dades, key=lambda t: t[0])
    for index, (_, item) in enumerate(dades_ordenades):
        taula.move(item, '', index)
    taula.heading(columna, command=lambda: ordenar_taula(taula, columna))

# Funció per manejar el doble clic
def on_double_click_busqueda(event):
    passar_a_seleccio()

def on_double_click_seleccio(event):
    treure_de_seleccio()

# Configuració de la finestra principal
ventana = tk.Tk()
ventana.title("Donar de Baixa Clients")
ventana.geometry("800x600")

frame_busqueda = tk.Frame(ventana)
frame_busqueda.pack(fill="x", padx=10, pady=5)

etiqueta_busqueda = tk.Label(frame_busqueda, text="Cercar:")
etiqueta_busqueda.pack(side="left")

entrada_busqueda = tk.Entry(frame_busqueda)
entrada_busqueda.pack(side="left", fill="x", expand=True, padx=5)

# Vincular el evento de entrada para buscar automáticamente
entrada_busqueda.bind("<KeyRelease>", buscar_clientes)

frame_tablas = tk.Frame(ventana)
frame_tablas.pack(fill="both", expand=True, padx=10, pady=5)

# Taula de cerca
tabla_busqueda = ttk.Treeview(frame_tablas, columns =("ID", "DNI", "Nom", "Activitats"), show="headings")
tabla_busqueda.heading("ID", text="ID")
tabla_busqueda.heading("DNI", text="DNI", command=lambda: ordenar_taula(tabla_busqueda, "DNI"))
tabla_busqueda.heading("Nom", text="Nom", command=lambda: ordenar_taula(tabla_busqueda, "Nom"))
tabla_busqueda.heading("Activitats", text="Activitats", command=lambda: ordenar_taula(tabla_busqueda, "Activitats"))
tabla_busqueda.column("ID", width=0)  # Ocultar columna ID
tabla_busqueda.column("DNI", width=100)
tabla_busqueda.column("Nom", width=100)
tabla_busqueda.column("Activitats", width=100)

tabla_busqueda.pack(side="left", fill="both", expand=True)

scroll_busqueda = ttk.Scrollbar(frame_tablas, orient="vertical", command=tabla_busqueda.yview)
tabla_busqueda.configure(yscroll=scroll_busqueda.set)
scroll_busqueda.pack(side="left", fill="y")

# Vincular l'esdeveniment de doble clic
tabla_busqueda.bind("<Double-1>", on_double_click_busqueda)

# Botons entre taules
frame_botons = tk.Frame(frame_tablas)
frame_botons.pack(side="left", padx=5)

boton_pasar = tk.Button(frame_botons, text=">>", command=passar_a_seleccio)
boton_pasar.pack(pady=5)

boton_quitar = tk.Button(frame_botons, text="<<", command=treure_de_seleccio)
boton_quitar.pack(pady=5)

# Taula de selecció
seleccio = ttk.Treeview(frame_tablas, columns=("ID", "DNI", "Nom", "Activitats"), show="headings")
seleccio.heading("ID", text="ID")
seleccio.heading("DNI", text="DNI")
seleccio.heading("Nom", text="Nom")
seleccio.heading("Activitats", text="Activitats")
seleccio.column("ID", width=0)  # Ocultar columna ID
seleccio.column("DNI", width=100)
seleccio.column("Nom", width=100)
seleccio.column("Activitats", width=100)

seleccio.pack(side="left", fill="both", expand=True)

scroll_seleccio = ttk.Scrollbar(frame_tablas, orient="vertical", command=seleccio.yview)
seleccio.configure(yscroll=scroll_seleccio.set)
scroll_seleccio.pack(side="left", fill="y")

# Vincular l'esdeveniment de doble clic
seleccio.bind("<Double-1>", on_double_click_seleccio)

# Botó per realitzar baixes
boton_bajas = tk.Button(ventana, text="Donar de Baixa", command=realitzar_baixes)
boton_bajas.pack(pady=10)

# Botó per generar el PDF
boton_pdf_baixes = tk.Button(ventana, text="Generar PDF Baixes", command=generar_pdf_baixes)
boton_pdf_baixes.pack(pady=10)

# Carregar dades a l'iniciar
buscar_clientes()

ventana.mainloop()
