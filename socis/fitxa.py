import subprocess
import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk, ImageFile
import mysql.connector
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
import tempfile
import os
import configparser

# Conexión a la base de datos MySQL usando config.ini
def conectar_db():
    config = configparser.ConfigParser()
    config.read('config.ini')
    
    return mysql.connector.connect(
        host=config['mysql']['host'],
        user=config['mysql']['user'],
        password=config['mysql']['password'],
        database=config['mysql']['database']
    )

# Permitir cargar imágenes truncadas
ImageFile.LOAD_TRUNCATED_IMAGES = True

# Función para convertir valores binarios (0/1) en "Sí"/"No"
def convertir_binario(valor):
    return "Sí" if valor == 1 else "No"

# Función para generar y abrir un PDF con los datos del socio
def generar_pdf(socio):
    try:
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
        pdf_path = temp_file.name
        temp_file.close()

        c = canvas.Canvas(pdf_path, pagesize=letter)
        c.setFont("Helvetica", 12)

        # Título
        c.drawString(30, 750, "Ficha del Socio")
        c.drawString(30, 740, "=" * 50)

        # Incluir la foto en la esquina superior derecha
        if socio.get("Foto"):
            try:
                foto = Image.open(BytesIO(socio["Foto"]))
                foto = foto.resize((100, 130), Image.Resampling.LANCZOS)
                foto_reader = ImageReader(foto)
                c.drawImage(foto_reader, 450, 650, width=100, height=130)
            except Exception:
                c.drawString(450, 750, "Foto no disponible")

        # Mostrar los datos (excluyendo los campos específicos)
        y = 700
        for campo, valor in socio.items():
            if campo in ["DNI", "Foto", "data_modificacio", "Descompte", "Temps_descompte", "Extres"]:
                continue
            if isinstance(valor, int) and valor in [0, 1]:
                valor = convertir_binario(valor)
            c.drawString(30, y, f"{campo}: {valor}")
            y -= 20

        c.save()

        # Abrir el PDF
        if os.name == 'nt':
            os.startfile(pdf_path)
        elif os.name == 'posix':
            opener = "open" if subprocess.run(["uname"], capture_output=True).stdout.strip() == b'Darwin' else "xdg-open"
            subprocess.run([opener, pdf_path])
        else:
            messagebox.showinfo("PDF Generado", f"El PDF se generó correctamente: {pdf_path}")
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo generar el PDF. Detalles: {str(e)}")

# Mostrar detalles del socio seleccionado
def mostrar_detalles(dni_soci):
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM socis WHERE DNI = %s", (dni_soci,))
    socio = cursor.fetchone()

    if not socio:
        messagebox.showerror("Error", "Socio no encontrado.")
        return

    detalles_ventana = tk.Toplevel(root)
    detalles_ventana.title(f"Detalles del socio: {socio['Nom']}")
    detalles_ventana.geometry("600x400")
    detalles_ventana.resizable(False, False)

    if socio['Foto']:
        try:
            foto = Image.open(BytesIO(socio['Foto']))
            foto = foto.resize((120, 120), Image.Resampling.LANCZOS)
            img = ImageTk.PhotoImage(foto)
            tk.Label(detalles_ventana, image=img).place(x=450, y=20)
            detalles_ventana.image = img
        except Exception:
            tk.Label(detalles_ventana, text="Error al cargar la foto").place(x=450, y=20)
    else:
        tk.Label(detalles_ventana, text="No hay foto disponible").place(x=450, y=20)

    tk.Label(detalles_ventana, text="Ficha del Socio", font=("Arial", 14)).place(x=20, y=20)
    y_pos = 60
    for campo, valor in socio.items():
        if campo in ["DNI", "Foto", "data_modificacio", "Descompte", "Temps_descompte", "Extres"]:
            continue
        if isinstance(valor, int) and valor in [0, 1]:
            valor = convertir_binario(valor)
        tk.Label(detalles_ventana, text=f"{campo}: {valor}", anchor="w").place(x=20, y=y_pos)
        y_pos += 20

    boton_pdf = tk.Button(detalles_ventana, text="Generar PDF", command=lambda: generar_pdf(socio))
    boton_pdf.place(x=250, y=350)

# Cargar datos para la tabla
def cargar_datos(busqueda=""):
    query = "SELECT DNI, Nom FROM socis WHERE Nom LIKE %s"
    cursor = conn.cursor()
    cursor.execute(query, (f"%{busqueda}%",))
    return cursor.fetchall()

# Actualizar la tabla según la búsqueda
def actualizar_tabla(*args):
    busqueda = entry_buscar.get()
    datos = cargar_datos(busqueda)
    for row in tree.get_children():
        tree.delete(row)
    for row in datos:
        tree.insert("", "end", values=row)

# Ordenar columnas de la tabla
def ordenar_tabla(columna):
    global datos_mostrados
    reverse = not orden[columna]  # Alternar orden
    datos_mostrados = sorted(datos_mostrados, key=lambda x: x[tree["columns"].index(columna)], reverse=reverse)
    orden[columna] = reverse

    # Actualizar la tabla con los datos ordenados
    for row in tree.get_children():
        tree.delete(row)
    for row in datos_mostrados:
        tree.insert("", "end", values=row)

def configurar_estilo():
    style = ttk.Style()
    style.configure("Treeview", font=("Arial", 12), rowheight=25)
    style.configure("Treeview.Heading", font=("Arial Bold", 12))
    style.configure("TLabel", font=("Arial", 12))
    style.configure("TButton", font=("Arial", 12))

conn = conectar_db()

root = tk.Tk()
root.title("Fitxes")
root.geometry("800x500")

# Configurar estilo
configurar_estilo()

# Barra de título
frame_titulo = tk.Frame(root, bg="#0078D7", height=50)
frame_titulo.pack(fill=tk.X)
tk.Label(frame_titulo, text="Fitxes", bg="#0078D7", fg="white", font=("Arial Bold", 16)).pack(pady=10)

frame_buscar = tk.Frame(root, bg="#F1F1F1", pady=10)
frame_buscar.pack(fill=tk.X)
tk.Label(frame_buscar, text="Buscar por nombre:", font=("Arial", 12), bg="#F1F1F1").pack(side=tk.LEFT, padx=5)
entry_buscar = tk.Entry(frame_buscar, font=("Arial", 12), width=40)
entry_buscar.pack(side=tk.LEFT, padx=5)
entry_buscar.bind("<KeyRelease>", actualizar_tabla)

tree = ttk.Treeview(root, columns=("DNI", "Nom"), show="headings", style="Treeview")
tree.heading("DNI", text="DNI", command=lambda: ordenar_tabla("DNI"))
tree.heading("Nom", text="Nombre", command=lambda: ordenar_tabla("Nom"))
tree.pack(fill=tk.BOTH, expand=True, pady=10)
tree.bind("<Double-1>", lambda event: mostrar_detalles(tree.item(tree.focus())["values"][0]))

datos_mostrados = cargar_datos()
orden = {"DNI": False, "Nom": False}

for row in datos_mostrados:
    tree.insert("", "end", values=row)

root.mainloop()
conn.close()
