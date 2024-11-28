import os
import shutil
import tkinter as tk
from tkinter import messagebox, filedialog
from PIL import Image, ImageTk
import mysql.connector
from mysql.connector import Error

# Variable global para la vista previa del logo
logo_preview_label = None

# Función para crear la base de datos y la tabla
def create_database():
    try:
        connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password=''  # Cambia esto según sea necesario
        )
        cursor = connection.cursor()
        cursor.execute("CREATE DATABASE IF NOT EXISTS gimnas")
        connection.database = 'gimnas'
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS Empresa (
                id INT AUTO_INCREMENT PRIMARY KEY,
                nom VARCHAR(100),
                adresa VARCHAR(255),
                poblacio VARCHAR(100),
                provincia VARCHAR(100),
                codi_postal VARCHAR(10),
                telefon VARCHAR(15),
                mobil VARCHAR(15),
                email VARCHAR(100),
                pagina_web VARCHAR(100),
                cif_nif VARCHAR(20)
            )
        """)
        connection.commit()
    except Error as e:
        messagebox.showerror("Error", str(e))
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

# Función para obtener datos existentes de la base de datos
def fetch_data():
    try:
        connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password='',
            database='gimnas'
        )
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM Empresa LIMIT 1")
        result = cursor.fetchone()
        return result
    except Error as e:
        messagebox.showerror("Error", str(e))
        return None
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

# Función para insertar o actualizar datos en la base de datos
def upsert_data(nom, adresa, poblacio, provincia, codi_postal, telefon, mobil, email, pagina_web, cif_nif):
    try:
        connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password='',
            database='gimnas'
        )
        cursor = connection.cursor()
        cursor.execute("SELECT COUNT(*) FROM Empresa")
        count = cursor.fetchone()[0]
        
        if count == 0:
            cursor.execute("""
                INSERT INTO Empresa (nom, adresa, poblacio, provincia, codi_postal, telefon, mobil, email, pagina_web, cif_nif)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (nom, adresa, poblacio, provincia, codi_postal, telefon, mobil, email, pagina_web, cif_nif))
        else:
            cursor.execute("""
                UPDATE Empresa
                SET nom=%s, adresa=%s, poblacio=%s, provincia=%s, codi_postal=%s, telefon=%s, mobil=%s, email=%s, pagina_web=%s, cif_nif=%s
                WHERE id=(SELECT id FROM Empresa LIMIT 1)
            """, (nom, adresa, poblacio, provincia, codi_postal, telefon, mobil, email, pagina_web, cif_nif))
        
        connection.commit()
        messagebox.showinfo("Èxit", "Registre actualitzat correctament.")
    except Error as e:
        messagebox.showerror("Error", str(e))
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

# Función para subir el logo
def upload_logo():
    logo_path = filedialog.askopenfilename(title="Selecciona el logo", filetypes=[("Imatges", "*.png;*.jpg;*.jpeg")])
    if logo_path:
        os.makedirs('logo', exist_ok=True)
        destination_path = 'logo/logo.jpg'
        
        if os.path.exists(destination_path):
            overwrite = messagebox.askyesno("Sobrescriure", "Ja existeix un logo. Vols sobrescriure'l?")
            if not overwrite:
                return
            os.remove(destination_path)
        
        shutil.copy(logo_path, destination_path)
        messagebox.showinfo("Èxit", "Logo pujat correctament.")
        show_logo_preview()

# Función para mostrar la vista previa del logo
def show_logo_preview():
    global logo_preview_label
    if os.path.exists('logo/logo.jpg'):
        img = Image.open('logo/logo.jpg')
        img.thumbnail((150, 150))
        photo = ImageTk.PhotoImage(img)
        if logo_preview_label is not None:
            logo_preview_label.config(image=photo)
            logo_preview_label.image = photo
        else:
            logo_preview_label = tk.Label(frame_logo, image=photo, bg="white")
            logo_preview_label.image = photo
            logo_preview_label.pack()

# Función para manejar el envío del formulario
def submit_form():
    nom = entry_nom.get()
    adresa = entry_adresa.get()
    poblacio = entry_poblacio.get()
    provincia = entry_provincia.get()
    codi_postal = entry_codi_postal.get()
    telefon = entry_telefon.get()
    mobil = entry_mobil.get()
    email = entry_email.get()
    pagina_web = entry_pagina_web.get()
    cif_nif = entry_cif_nif.get()
    
    upsert_data(nom, adresa, poblacio, provincia, codi_postal, telefon, mobil, email, pagina_web, cif_nif)

# Ventana principal
root = tk.Tk()
root.title("Registre d'Empresa")
root.configure(bg="#f4f4f4")

# Crear el marco del formulario
frame_form = tk.Frame(root, bg="#f4f4f4")
frame_form.pack(pady=10, padx=10, fill="both", expand=True)

# Etiquetas y entradas en dos columnas
fields = [
    ("Nom", "entry_nom"),
    ("Adreça", "entry_adresa"),
    ("Població", "entry_poblacio"),
    ("Província", "entry_provincia"),
    ("Codi Postal", "entry_codi_postal"),
    ("Telèfon", "entry_telefon"),
    ("Mòbil", "entry_mobil"),
    ("Email", "entry_email"),
    ("Pàgina Web", "entry_pagina_web"),
    ("CIF/NIF", "entry_cif_nif"),
]
entries = {}

# Crear dos columnas de campos
for i, (label_text, var_name) in enumerate(fields):
    row = i // 2
    col = i % 2
    frame = tk.Frame(frame_form, bg="#f4f4f4")
    frame.grid(row=row, column=col, padx=10, pady=5, sticky="w")

    label = tk.Label(frame, text=label_text, font=("Arial", 10, "bold"), bg="#f4f4f4")
    label.pack(anchor="w")

    entry = tk.Entry(frame, font=("Arial", 12), width=30)
    entry.pack(pady=5)
    entries[var_name] = entry

entry_nom, entry_adresa, entry_poblacio, entry_provincia, entry_codi_postal, entry_telefon, entry_mobil, entry_email, entry_pagina_web, entry_cif_nif = (
    entries["entry_nom"],
    entries["entry_adresa"],
    entries["entry_poblacio"],
    entries["entry_provincia"],
    entries["entry_codi_postal"],
    entries["entry_telefon"],
    entries["entry_mobil"],
    entries["entry_email"],
    entries["entry_pagina_web"],
    entries["entry_cif_nif"],
)

# Marco para el logo
frame_logo = tk.Frame(root, bg="white", relief="ridge", bd=2)
frame_logo.pack(pady=10, ipadx=20, ipady=20, fill="x")

# Botones
frame_buttons = tk.Frame(root, bg="#f4f4f4")
frame_buttons.pack(pady=10)

tk.Button(frame_buttons, text="Afegir Logo", font=("Arial", 12), command=upload_logo, bg="#007BFF", fg="white", width=20).pack(pady=5)
tk.Button(frame_buttons, text="Registrar Empresa", font=("Arial", 12), command=submit_form, bg="#28A745", fg="white", width=20).pack(pady=5)

# Permitir que la ventana ajuste su tamaño dinámicamente
root.grid_columnconfigure(0, weight=1)
root.grid_rowconfigure(0, weight=1)

# Inicializar la base de datos y crear la tabla
create_database()

# Obtener los datos existentes y llenar los campos
data = fetch_data()
if data:
    entry_nom.insert(0, data[1])
    entry_adresa.insert(0, data[2])
    entry_poblocio.insert(0, data[3])
    entry_provincia.insert(0, data[4])
    entry_codi_postal.insert(0, data[5])
    entry_telefon.insert(0, data[6])
    entry_mobil.insert(0, data[7])
    entry_email.insert(0, data[8])
    entry_pagina_web.insert(0, data[9])
    entry_cif_nif.insert(0, data[10])

show_logo_preview()

# Iniciar la aplicación
root.mainloop()
