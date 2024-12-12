import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import mysql.connector
from datetime import datetime
import subprocess
import os
import sys

# Conexión a la base de datos
def connect_db():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="gimnas"
    )

# Función para obtener las facturas filtradas
def obtenir_factures(filtro_mes=None, filtro_anio=None, tipo_cliente="Ambos"):
    conn = connect_db()
    cursor = conn.cursor(dictionary=True)

    # Consulta SQL base
    query = """
        SELECT f.numero_factura, s.Nom as client, f.total, f.fecha
        FROM facturas f
        JOIN socis s ON f.cliente_id = s.ID
    """
    # Agregar filtros si existen
    params = []
    if filtro_anio:
        query += " WHERE YEAR(f.fecha) = %s"
        params.append(filtro_anio)
    if filtro_mes:
        if params:  # Si ya hay un filtro de año, agregamos AND
            query += " AND MONTH(f.fecha) = %s"
        else:
            query += " WHERE MONTH(f.fecha) = %s"
        params.append(filtro_mes)
    if tipo_cliente != "Ambos":
        if params:  # Si ya hay filtros, agregamos AND
            query += " AND f.tipo_cliente = %s"
        else:
            query += " WHERE f.tipo_cliente = %s"
        params.append(tipo_cliente)

    cursor.execute(query, tuple(params))
    factures = cursor.fetchall()
    cursor.close()
    conn.close()
    return factures

# Función para verificar si ya existe una factura rectificativa
def existeix_rectificativa(numero_factura):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM facturas WHERE numero_factura = %s", (f"R{numero_factura}",))
    count = cursor.fetchone()[0]
    cursor.close()
    conn.close()
    return count > 0

# Función para actualizar la tabla y mostrar el total facturado
def actualitzar_taula():
    filtro_mes = mes_combobox.get()
    filtro_anio = anio_combobox.get()
    tipo_cliente = tipo_cliente_combobox.get()

    # Si no se seleccionan valores, mostrar todas las facturas
    factures = obtenir_factures(
        filtro_mes=None if filtro_mes == "Tots" else int(filtro_mes),
        filtro_anio=None if filtro_anio == "Tots" else int(filtro_anio),
        tipo_cliente=tipo_cliente
    )

    # Limpiar la tabla antes de agregar los nuevos datos
    for row in tabla.get_children():
        tabla.delete(row)

    # Agregar las nuevas filas a la tabla
    total_facturat = 0
    for factura in factures:
        tabla.insert("", "end", values=(factura['numero_factura'], factura['client'], factura['total'], factura['fecha']))
        total_facturat += factura['total']

    # Mostrar el total facturado
    total_label.config(text=f"Total facturat: {total_facturat:.2f} €")

# Función para generar una factura rectificativa
def generar_factura_rectificativa():
    selected_item = tabla.selection()
    if not selected_item:
        messagebox.showerror("Error", "Heu de seleccionar una factura per generar la rectificativa.")
        return

    # Obtener los datos de la factura seleccionada
    factura = tabla.item(selected_item, "values")
    numero_factura = factura[0]
    client = factura[1]
    total = factura[2]  # Aquí es donde obtenemos el total como cadena

    # Convertir el total a un número (float) para poder invertirlo
    try:
        total = float(total)
    except ValueError:
        messagebox.showerror("Error", "El total de la factura no és un valor numèric vàlid.")
        return

    # Verificar si ya existe una factura rectificativa para esta factura
    if existeix_rectificativa(numero_factura):
        messagebox.showerror("Error", "Ja s'ha generat una factura rectificativa per aquesta factura.")
        return

    # Generar la factura rectificativa
    numero_factura_rectificativa = "R" + numero_factura
    conn = connect_db()
    cursor = conn.cursor()

    # Insertar la factura rectificativa con el monto negativo
    cursor.execute("""
        INSERT INTO facturas (numero_factura, cliente_id, total, fecha, tipo_cliente)
        SELECT %s, cliente_id, %s, NOW(), tipo_cliente
        FROM facturas
        WHERE numero_factura = %s
    """, (numero_factura_rectificativa, -total, numero_factura))
    conn.commit()

    # Confirmación de que la factura rectificativa fue generada
    messagebox.showinfo("Factura rectificativa", f"Factura rectificativa generada amb número {numero_factura_rectificativa}.")

    cursor.close()
    conn.close()

    # Actualizar la tabla
    actualitzar_taula()

# Función para eliminar una factura
def eliminar_factura():
    selected_item = tabla.selection()
    if not selected_item:
        messagebox.showerror("Error", "Heu de seleccionar una factura per eliminar.")
        return

    # Obtener los datos de la factura seleccionada
    factura = tabla.item(selected_item, "values")
    numero_factura = factura[0]

    # Verificar si el número de factura empieza con 'R'
    if not numero_factura.startswith('R'):
        messagebox.showerror("Error", "Només es poden eliminar factures rectificatives que comencen amb 'R'.")
        return

    # Confirmar la eliminación
    resposta = messagebox.askyesno("Confirmar", f"Esteu segur que voleu eliminar la factura {numero_factura}?")
    if resposta:
        conn = connect_db()
        cursor = conn.cursor()

        # Eliminar la factura de la base de datos
        cursor.execute("DELETE FROM facturas WHERE numero_factura = %s", (numero_factura,))
        conn.commit()

        # Confirmación de la eliminación
        messagebox.showinfo("Eliminació", f"Factura {numero_factura} eliminada correctament.")

        cursor.close()
        conn.close()

        # Actualizar la tabla
        actualitzar_taula()

# Función para abrir el PDF de la factura seleccionada
def abrir_factura_pdf():
    selected_item = tabla.selection()
    if not selected_item:
        messagebox.showerror("Error", "Heu de seleccionar una factura per obrir el PDF.")
        return

    # Obtener el número de factura
    factura = tabla.item(selected_item, "values")
    numero_factura = factura[0]

    # Construir la ruta del script y pasar el número de factura como argumento
    try:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        script_path = os.path.join(current_dir, 'generar_factura.py')
        subprocess.run([sys.executable, script_path, numero_factura], check=True)
    except subprocess.CalledProcessError as e:
        messagebox.showerror("Error", f"Error al ejecutar generar_factura.py: {e}")
    except FileNotFoundError:
        messagebox.showerror("Error", "El archivo generar_factura.py no se encuentra.")

# Función para ejecutar el script novafactura.py
def ejecutar_novafactura():
    try:
        # Obtener la ruta del directorio actual
        current_dir = os.path.dirname(os.path.abspath(__file__))
        # Construir la ruta completa al script
        script_path = os.path.join(current_dir, 'novafactura.py')
        # Ejecutar el script
        subprocess.run([sys.executable, script_path], check=True)
    except subprocess.CalledProcessError as e:
        messagebox.showerror("Error", f"Error al ejecutar novafactura.py: {e}")
    except FileNotFoundError:
        messagebox.showerror("Error", "El archivo novafactura.py no se encuentra.")

# Crear la ventana principal
ventana = tk.Tk()
ventana.title("Factures")

# Crear los filtros
filtro_frame = tk.Frame(ventana)
filtro_frame.pack(pady=20)

# Mes
tk.Label(filtro_frame, text="Mes:").grid(row=0, column=0, padx=10)
mes_combobox = ttk.Combobox(filtro_frame, values=["Tots"] + [str(i) for i in range(1, 13)])
mes_combobox.set("Tots")  # Mostrar "Tots" como valor predeterminado
mes_combobox.grid(row=0, column=1)

# Año
tk.Label(filtro_frame, text="Any:").grid(row=0, column=2, padx=10)
anio_combobox = ttk.Combobox(filtro_frame, values=["Tots"] + [str(i) for i in range(2020, datetime.now().year + 1)])
anio_combobox.set("Tots")  # Mostrar "Tots" como valor predeterminado
anio_combobox.grid(row=0, column=3)

# Tipo de cliente
tk.Label(filtro_frame, text="Tipus de client:").grid(row=1, column=0, padx=10)
tipo_cliente_combobox = ttk.Combobox(filtro_frame, values=["Ambos", "socis", "esporadics"])
tipo_cliente_combobox.set("Ambos")  # Mostrar ambos tipos por defecto
tipo_cliente_combobox.grid(row=1, column=1)

# Botón para actualizar la tabla
actualizar_button = tk.Button(filtro_frame, text="Filtrar", command=actualitzar_taula)
actualizar_button.grid(row=1, column=2, padx=10)

# Tabla para mostrar las facturas
tabla_frame = tk.Frame(ventana)
tabla_frame.pack(pady=20)

tabla = ttk.Treeview(tabla_frame, columns=("numero_factura", "cliente", "total", "fecha"), show="headings")
tabla.heading("numero_factura", text="Número Factura")
tabla.heading("cliente", text="Client")
tabla.heading("total", text="Total")
tabla.heading("fecha", text="Fecha")
tabla.pack()

# Botones de acción
acciones_frame = tk.Frame(ventana)
acciones_frame.pack(pady=20)

rectificativa_button = tk.Button(acciones_frame, text="Generar Factura Rectificativa", command=generar_factura_rectificativa)
rectificativa_button.pack(side=tk.LEFT, padx=10)

eliminar_button = tk.Button(acciones_frame, text="Eliminar Factura", command=eliminar_factura)
eliminar_button.pack(side=tk.LEFT, padx=10)

abrir_pdf_button = tk.Button(acciones_frame, text="Obrir PDF", command=abrir_factura_pdf)
abrir_pdf_button.pack(side=tk.LEFT, padx=10)

novafactura_button = tk.Button(acciones_frame, text="Nova Factura", command=ejecutar_novafactura)
novafactura_button.pack(side=tk.LEFT, padx=10)

# Total facturado
total_label = tk.Label(ventana, text="Total facturat: 0.00 €", fg="red")
total_label.pack(pady=10)

# Llamar a actualitzar_taula al inicio para cargar todas las facturas
actualitzar_taula()

ventana.mainloop()
