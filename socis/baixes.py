import tkinter as tk
from tkinter import ttk, messagebox
import mysql.connector
from datetime import date

# Conexión a la base de datos
def conectar_bd():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="gimnas"
    )

def buscar_clientes():
    criterio = entrada_busqueda.get()
    query = """
        SELECT ID, DNI, Nom, Activitats 
        FROM socis 
        WHERE Activitats IS NOT NULL AND (DNI LIKE %s OR Nom LIKE %s)
    """
    valores = (f"%{criterio}%", f"%{criterio}%")
    conexion = conectar_bd()
    cursor = conexion.cursor()
    cursor.execute(query, valores)
    resultados = cursor.fetchall()
    conexion.close()

    for row in tabla_busqueda.get_children():
        tabla_busqueda.delete(row)

    for resultado in resultados:
        tabla_busqueda.insert("", "end", values=resultado)

def pasar_a_seleccion():
    for item in tabla_busqueda.selection():
        valores = tabla_busqueda.item(item, "values")
        if not any(valores[0] == seleccion.item(child, "values")[0] for child in seleccion.get_children()):
            seleccion.insert("", "end", values=valores)
        tabla_busqueda.delete(item)  # Eliminar de la tabla de búsqueda

def quitar_de_seleccion():
    for item in seleccion.selection():
        valores = seleccion.item(item, "values")
        tabla_busqueda.insert("", "end", values=valores)  # Devolver a la tabla de búsqueda
        seleccion.delete(item)  # Eliminar de la tabla de selección

def realizar_bajas():
    confirmacion = messagebox.askyesno("Confirmar", "¿Estás seguro de realizar las bajas seleccionadas?")
    if not confirmacion:
        return

    ids_seleccionados = [seleccion.item(item, "values")[0] for item in seleccion.get_children()]
    if not ids_seleccionados:
        messagebox.showwarning("Advertencia", "No has seleccionado ningún cliente.")
        return

    query = """
        UPDATE socis 
        SET Activitats = NULL, Baixa = %s 
        WHERE ID = %s
    """
    conexion = conectar_bd()
    cursor = conexion.cursor()
    fecha_hoy = date.today().strftime("%Y-%m-%d")

    for id_cliente in ids_seleccionados:
        cursor.execute(query, (fecha_hoy, id_cliente))

    conexion.commit()
    conexion.close()

    messagebox.showinfo("Èxit", "Les baixes es van realitzar correctament.")
    buscar_clientes()
    for row in seleccion.get_children():
        seleccion.delete(row)

# Función para ordenar tabla
def ordenar_tabla(tabla, columna):
    datos = [(tabla.set(item, columna), item) for item in tabla.get_children('')]
    datos_ordenados = sorted(datos, key=lambda t: t[0])
    for index, (_, item) in enumerate(datos_ordenados):
        tabla.move(item, '', index)
    tabla.heading(columna, command=lambda: ordenar_tabla(tabla, columna))

# Configuración de la ventana principal
ventana = tk.Tk()
ventana.title("Baixa Clients")
ventana.geometry("800x600")

frame_busqueda = tk.Frame(ventana)
frame_busqueda.pack(fill="x", padx=10, pady=5)

etiqueta_busqueda = tk.Label(frame_busqueda, text="Buscar:")
etiqueta_busqueda.pack(side="left")

entrada_busqueda = tk.Entry(frame_busqueda)
entrada_busqueda.pack(side="left", fill="x", expand=True, padx=5)

boton_buscar = tk.Button(frame_busqueda, text="Buscar", command=buscar_clientes)
boton_buscar.pack(side="left")

frame_tablas = tk.Frame(ventana)
frame_tablas.pack(fill="both", expand=True, padx=10, pady=5)

# Tabla de búsqueda
tabla_busqueda = ttk.Treeview(frame_tablas, columns=("ID", "DNI", "Nom", "Activitats"), show="headings")
for col in ("ID", "DNI", "Nom", "Activitats"):
    tabla_busqueda.heading(col, text=col, command=lambda c=col: ordenar_tabla(tabla_busqueda, c))
    tabla_busqueda.column(col, width=100)

tabla_busqueda.pack(side="left", fill="both", expand=True)

scroll_busqueda = ttk.Scrollbar(frame_tablas, orient="vertical", command=tabla_busqueda.yview)
tabla_busqueda.configure(yscroll=scroll_busqueda.set)
scroll_busqueda.pack(side="left", fill="y")

# Botones entre tablas
frame_botones = tk.Frame(frame_tablas)
frame_botones.pack(side="left", padx=5)

boton_pasar = tk.Button(frame_botones, text=">>", command=pasar_a_seleccion)
boton_pasar.pack(pady=5)

boton_quitar = tk.Button(frame_botones, text="<<", command=quitar_de_seleccion)
boton_quitar.pack(pady=5)

# Tabla de selección
seleccion = ttk.Treeview(frame_tablas, columns=("ID", "DNI", "Nom", "Activitats"), show="headings")
for col in ("ID", "DNI", "Nom", "Activitats"):
    seleccion.heading(col, text=col)
    seleccion.column(col, width=100)

seleccion.pack(side="left", fill="both", expand=True)

scroll_seleccion = ttk.Scrollbar(frame_tablas, orient="vertical", command=seleccion.yview)
seleccion.configure(yscroll=scroll_seleccion.set)
scroll_seleccion.pack(side="left", fill="y")

# Botón para realizar bajas
boton_bajas = tk.Button(ventana, text="Baixa", command=realizar_bajas)
boton_bajas.pack(pady=10)

# Cargar datos al iniciar
buscar_clientes()

ventana.mainloop()
