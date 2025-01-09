import tkinter as tk
from tkinter import ttk, messagebox
import mysql.connector
from datetime import datetime
import configparser

# Función para leer la configuración de la base de datos desde config.ini
def leer_config():
    config = configparser.ConfigParser()
    config.read("config.ini")
    return config["mysql"]

# Conexión a la base de datos usando config.ini
def connect_db():
    config = leer_config()
    return mysql.connector.connect(
        host=config["host"],
        user=config["user"],
        password=config["password"],
        database=config["database"]
    )

# Función para obtener el último número de factura
def obtener_ultimo_numero_factura():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT numero_factura FROM facturas WHERE numero_factura NOT LIKE 'R%' ORDER BY numero_factura DESC LIMIT 1")
    ultimo_numero = cursor.fetchone()
    cursor.close()
    conn.close()

    if ultimo_numero:
        # Verificar si estamos en un nuevo año y si la última factura es de un año anterior
        last_year = int(ultimo_numero[0][:4])
        current_year = datetime.now().year

        # Si cambiamos de año, reiniciar la numeración de las facturas
        if last_year != current_year:
            return f"{current_year}-1"

        # Si estamos en el mismo año, extraer el número y sumarle 1
        numero = int(ultimo_numero[0].split('-')[1])  # Eliminar el año y convertir a entero
        return f"{current_year}-{numero + 1}"
    else:
        # Si no hay facturas, la primera factura será 1
        return f"{datetime.now().year}-1"

# Función para buscar el soci en las tablas socis o esporadics
def buscar_soci():
    # Obtener el nombre del soci desde el combobox
    soci = soci_combobox.get()

    conn = connect_db()
    cursor = conn.cursor()

    # Verificar en la tabla "socis"
    cursor.execute("SELECT ID, Nom FROM socis WHERE Nom LIKE %s", ('%' + soci + '%',))
    socis_resultados = cursor.fetchall()

    # Verificar en la tabla "esporadics"
    cursor.execute("SELECT ID, Nom FROM esporadics WHERE Nom LIKE %s", ('%' + soci + '%',))
    esporadics_resultados = cursor.fetchall()

    cursor.close()
    conn.close()

    # Mostrar los resultados en el combobox
    resultados = [f"{s[1]} (ID: {s[0]})" for s in socis_resultados + esporadics_resultados]

    # Si no hay resultados
    if not resultados:
        messagebox.showwarning("Advertencia", "No se encontraron socios o esporádicos con ese nombre.")
        return

    # Limpiar el combobox y agregar los resultados encontrados
    soci_combobox['values'] = resultados
    if resultados:
        soci_combobox.current(0)  # Seleccionar el primer resultado

# Función para calcular automáticamente el precio o el total
def actualizar_precio_o_total(*args):
    try:
        # Si el usuario cambia el precio sin IVA (preu)
        preu = preu_entry.get()
        if preu:
            preu = float(preu)
            total = preu * 1.21  # Calculamos el total con IVA al 21%
            total_entry.delete(0, tk.END)
            total_entry.insert(0, f"{total:.2f}")

            iva = total - preu  # Calculamos el IVA como la diferencia entre el total y el precio
            iva_entry.delete(0, tk.END)
            iva_entry.insert(0, f"{iva:.2f}")
        
        # Si el usuario cambia el total (con IVA)
        total = total_entry.get()
        if total:
            total = float(total)
            preu = total / 1.21  # Calculamos el precio sin IVA
            preu_entry.delete(0, tk.END)
            preu_entry.insert(0, f"{preu:.2f}")

            iva = total - preu  # Calculamos el IVA como la diferencia entre el total y el precio
            iva_entry.delete(0, tk.END)
            iva_entry.insert(0, f"{iva:.2f}")
    
    except ValueError:
        messagebox.showerror("Error", "Por favor ingrese valores válidos para el precio o el total.")

def crear_factura():
    # Obtener el soci seleccionado
    soci_seleccionado = soci_combobox.get()
    if not soci_seleccionado:
        messagebox.showerror("Error", "Debe seleccionar un soci.")
        return

    # Obtener la descripción de la factura
    descripcion = descripcion_text.get("1.0", tk.END).strip()

    if not descripcion:
        messagebox.showerror("Error", "Debe ingresar una descripción.")
        return

    # Obtener el precio sin IVA (preu)
    preu = preu_entry.get()
    if not preu:
        messagebox.showerror("Error", "Debe ingresar el precio sin IVA.")
        return

    preu = float(preu)

    # Obtener el total
    total = total_entry.get()
    if not total:
        messagebox.showerror("Error", "Debe ingresar el total de la factura.")
        return

    total = float(total)

    # Obtener el soci ID
    soci_id = soci_seleccionado.split("(ID: ")[1][:-1]  # Extraemos solo el ID del soci

    # Generar el número de factura
    numero_factura = obtener_ultimo_numero_factura()

    conn = connect_db()
    cursor = conn.cursor()

    # Insertar la nueva factura en la base de datos
    cursor.execute("""
        INSERT INTO facturas (numero_factura, cliente_id, activitats, fecha, preu, iva, total)
        VALUES (%s, %s, %s, NOW(), %s, %s, %s)
    """, (numero_factura, soci_id, descripcion, preu, 21, total))

    conn.commit()
    cursor.close()
    conn.close()

    messagebox.showinfo("Factura creada", f"Factura {numero_factura} creada correctamente.")

    # Limpiar los campos del formulario después de crear la factura
    soci_combobox.set("")  # Limpiar el combobox
    descripcion_text.delete("1.0", tk.END)  # Limpiar el campo de descripción
    preu_entry.delete(0, tk.END)  # Limpiar el campo de precio sin IVA
    iva_entry.delete(0, tk.END)  # Limpiar el campo de IVA
    total_entry.delete(0, tk.END)  # Limpiar el campo de total

# Crear la ventana para la nueva factura
ventana = tk.Tk()
ventana.title("Crear Nueva Factura")

# Campo para buscar el soci
tk.Label(ventana, text="Soci:").grid(row=0, column=0, padx=10, pady=10)
soci_combobox = ttk.Combobox(ventana)
soci_combobox.grid(row=0, column=1, padx=10, pady=10)
buscar_button = tk.Button(ventana, text="Buscar Soci", command=buscar_soci)
buscar_button.grid(row=0, column=2, padx=10, pady=10)

# Campo para la descripción de la factura
tk.Label(ventana, text="Descripció :").grid(row=1, column=0, padx=10, pady=10)
descripcion_text = tk.Text(ventana, height=4, width=40)
descripcion_text.grid(row=1, column=1, padx=10, pady=10)

# Campo para el precio sin IVA (Preu)
tk.Label(ventana, text="Preu:").grid(row=2, column=0, padx=10, pady=10)
preu_entry = tk.Entry(ventana, width=20)
preu_entry.grid(row=2, column=1, padx=10, pady=10)

# Campo para el IVA (fijo al 21%)
tk.Label(ventana, text="IVA 21 (%):").grid(row=3, column=0, padx=10, pady=10)
iva_entry = tk.Entry(ventana, width=20)
iva_entry.grid(row=3, column=1, padx=10, pady=10)

# Campo para el total (se calcula automáticamente)
tk.Label(ventana, text="Total (amb IVA):").grid(row=4, column=0, padx=10, pady=10)
total_entry = tk.Entry(ventana, width=20)
total_entry.grid(row=4, column=1, padx=10, pady=10)

# Vincular los cambios de los campos de precio y total para hacer los cálculos automáticos cuando el campo pierda el foco
preu_entry.bind("<FocusOut>", actualizar_precio_o_total)
total_entry.bind("<FocusOut>", actualizar_precio_o_total)

# Botón para crear la factura
crear_factura_button = tk.Button(ventana, text="Crear Factura", command=crear_factura)
crear_factura_button.grid(row=6, column=0, columnspan=3, pady=20)

# Ejecutar la ventana
ventana.mainloop()
