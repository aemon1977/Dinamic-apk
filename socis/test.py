import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry
import mysql.connector
import configparser

# Leer configuración desde un archivo `config.ini`
config = configparser.ConfigParser()
config.read('config.ini')

# Configuración de conexión a la base de datos
def conectar_db():
    return mysql.connector.connect(
        host=config['mysql']['host'],
        user=config['mysql']['user'],
        password=config['mysql']['password'],
        database=config['mysql']['database']
    )

# Función para cargar datos de la base de datos
def cargar_datos(busqueda=None):
    conn = conectar_db()
    cursor = conn.cursor(dictionary=True)
    query = "SELECT * FROM socis"
    if busqueda:
        query += " WHERE Nom LIKE %s OR DNI LIKE %s"
        cursor.execute(query, ('%' + busqueda + '%', '%' + busqueda + '%'))
    else:
        cursor.execute(query)
    rows = cursor.fetchall()
    conn.close()
    return rows

# Función para mostrar los datos en el Treeview
def mostrar_datos(tree, busqueda=None):
    for row in tree.get_children():
        tree.delete(row)
    for row in cargar_datos(busqueda):
        tree.insert('', 'end', values=tuple(row.values()))

# Ventana de búsqueda
def ventana_busqueda():
    def buscar():
        busqueda = entrada_busqueda.get()
        mostrar_datos(tree, busqueda)

    def abrir_modificacion():
        if not tree.selection():
            messagebox.showwarning("Selección", "Por favor, selecciona un registro para modificar.")
            return
        item = tree.item(tree.selection()[0])
        datos = item['values']
        ventana_modificacion(datos)

    ventana = tk.Tk()
    ventana.title("Búsqueda de Socios")
    ventana.geometry("800x500")

    # Entrada de búsqueda
    frame_busqueda = ttk.Frame(ventana)
    frame_busqueda.pack(pady=10)

    ttk.Label(frame_busqueda, text="Buscar:").pack(side=tk.LEFT, padx=5)
    entrada_busqueda = ttk.Entry(frame_busqueda, width=40)
    entrada_busqueda.pack(side=tk.LEFT, padx=5)
    ttk.Button(frame_busqueda, text="Buscar", command=buscar).pack(side=tk.LEFT, padx=5)

    # Tabla para mostrar resultados
    columnas = ["ID", "DNI", "Nom", "Carrer", "Codipostal", "Poblacio", "Provincia", "email", "Data_naixement"]
    tree = ttk.Treeview(ventana, columns=columnas, show='headings', height=15)
    for col in columnas:
        tree.heading(col, text=col)
        tree.column(col, width=100)
    tree.pack(pady=10, fill=tk.BOTH, expand=True)

    # Botón para abrir la ventana de modificación
    ttk.Button(ventana, text="Modificar", command=abrir_modificacion).pack(pady=10)

    mostrar_datos(tree)
    ventana.mainloop()

# Ventana de modificación
def ventana_modificacion(datos):
    ventana = tk.Toplevel()
    ventana.title("Modificar Socio")
    ventana.geometry("600x600")
    ventana.resizable(False, False)

    # Formulario para modificar datos
    frame_formulario = ttk.Frame(ventana, padding=20)
    frame_formulario.pack(fill=tk.BOTH, expand=True)

    campos = [
        ("DNI", "DNI"),
        ("Nom", "Nombre"),
        ("Carrer", "Calle"),
        ("Codipostal", "Código Postal"),
        ("Poblacio", "Población"),
        ("Provincia", "Provincia"),
        ("email", "Email"),
        ("Data_naixement", "Fecha de Nacimiento")
    ]
    entradas = {}

    for idx, (campo, etiqueta) in enumerate(campos):
        ttk.Label(frame_formulario, text=etiqueta).grid(row=idx, column=0, padx=10, pady=10, sticky="w")
        if campo == "Data_naixement":
            entrada = DateEntry(frame_formulario, width=20, date_pattern='yyyy-mm-dd')
        else:
            entrada = ttk.Entry(frame_formulario, width=40)
        entrada.grid(row=idx, column=1, padx=10, pady=10)
        entrada.insert(0, datos[idx + 1])  # Ignorar la columna ID
        entradas[campo] = entrada

    # Botón para guardar cambios
    def guardar():
        try:
            conn = conectar_db()
            cursor = conn.cursor()
            valores = [entradas[campo].get() for campo, _ in campos] + [datos[0]]  # ID al final
            query = f"UPDATE socis SET {', '.join([f'{campo}=%s' for campo, _ in campos])} WHERE ID=%s"
            cursor.execute(query, valores)
            conn.commit()
            conn.close()
            messagebox.showinfo("Éxito", "Cambios guardados correctamente.")
            ventana.destroy()
        except mysql.connector.Error as e:
            messagebox.showerror("Error", f"Error al guardar los cambios: {e}")

    # Botón de guardar
    ttk.Button(ventana, text="Guardar Cambios", command=guardar).pack(pady=20)

# Ejecutar la aplicación
ventana_busqueda()
