from tkinter import *
from tkinter import messagebox, ttk
from datetime import datetime
from decimal import Decimal
from tkcalendar import Calendar, DateEntry
import mysql.connector
from configparser import ConfigParser
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import subprocess  # Importar para ejecutar el script

# Función para leer la configuración de la base de datos
def leer_config():
    config = ConfigParser()
    config.read("config.ini")
    return config["mysql"]

# Conexión a la base de datos
def conectar_db():
    config = leer_config()
    return mysql.connector.connect(
        host=config.get("host", "localhost"),
        user=config.get("user", "root"),
        password=config.get("password", ""),
        database=config.get("database", "gimnas")
    )

# Clase principal de la aplicación
class FacturacionApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Sistema de Facturación")

        # Variables para actualizar dinámicamente
        self.cantidad_sin_iva = StringVar(value="0.00")
        self.iva_calculado = StringVar(value="0.00")
        self.total_con_iva = StringVar(value="0.00")

        # Obtener el número de factura antes de crear la interfaz
        self.numero_factura = self.obtener_numero_factura()

        # Crear interfaz
        self.crear_widgets()

    def crear_widgets(self):
        # Frame para la selección de cliente
        self.frame_cliente = LabelFrame(self.root, text="Seleccionar Cliente")
        self.frame_cliente.pack(padx=10, pady=10)

        self.tipo_cliente = StringVar(value="socis")
        Radiobutton(self.frame_cliente, text="Socis", variable=self.tipo_cliente, value="socis", command=self.cargar_clientes).pack(side=LEFT)
        Radiobutton(self.frame_cliente, text="Esporádics", variable=self.tipo_cliente, value="esporadics", command=self.cargar_clientes).pack(side=LEFT)

        self.combo_clientes = ttk.Combobox(self.frame_cliente)
        self.combo_clientes.pack(padx=10, pady=10)
        self.combo_clientes.bind("<<ComboboxSelected>>", self.cargar_detalle_cliente)
        self.combo_clientes.bind("<KeyRelease>", lambda event: self.buscar_cliente())

        self.buscar_button = Button(self.frame_cliente, text="Buscar", command=self.buscar_cliente)
        self.buscar_button.pack(side=LEFT)

        # Frame para la factura
        self.frame_factura = LabelFrame(self.root, text="Factura")
        self.frame_factura.pack(padx=10, pady=10)

        Label(self.frame_factura, text="Número de Factura:").grid(row=0, column=0)
        self.numero_factura_entry = Entry(self.frame_factura)
        self.numero_factura_entry.insert(0, str(self.numero_factura))  # Valor por defecto
        self.numero_factura_entry.grid(row=0, column=1)

        Label(self.frame_factura, text="Fecha de la Factura:").grid(row=1, column=0)
        self.fecha_entry = DateEntry(self.frame_factura, width=12, bg="darkblue", fg="white", borderwidth=2, date_pattern='dd-mm-yyyy')
        self.fecha_entry.set_date(datetime.now())
        self.fecha_entry.grid(row=1, column=1)

        Label(self.frame_factura, text="Actividades:").grid(row=2, column=0)
        self.actividades_text = Text(self.frame_factura, height=5, width=40)
        self.actividades_text.grid(row=2, column=1)

        Label(self.frame_factura, text="Preu:").grid(row=3, column=0)
        self.cantidad_label = Label(self.frame_factura, textvariable=self.cantidad_sin_iva)
        self.cantidad_label.grid(row=3, column=1)

        Label(self.frame_factura, text="IVA (%):").grid(row=4, column=0)
        self.iva_entry = Entry(self.frame_factura)
        self.iva_entry.insert(0, "21")  # Valor por defecto
        self.iva_entry.grid(row=4, column=1)

        # Etiquetas para mostrar los resultados
        Label(self.frame_factura, text="IVA:").grid(row=5, column=0)
        self.iva_label = Label(self.frame_factura, textvariable=self.iva_calculado)
        self.iva_label.grid(row=5, column=1)

        Label(self.frame_factura, text="Total:").grid(row=6, column=0)
        self.total_con_iva_label = Label(self.frame_factura, textvariable=self.total_con_iva)
        self.total_con_iva_label.grid(row=6, column=1)

        self.boton_guardar = Button(self.frame_factura, text="Guardar Factura", command=self.guardar_factura)
        self.boton_guardar.grid(row=7, columnspan=2)

        # Cargar clientes al iniciar
        self.cargar_clientes()

    def obtener_numero_factura(self):
        db = conectar_db()
        cursor = db.cursor()
        cursor.execute("SELECT ultimo_numero, año FROM configuracion ORDER BY id DESC LIMIT 1")
        result = cursor.fetchone()

        if result:
            ultimo_numero, año = result
            current_year = datetime.now().year
            if año != current_year:
                nuevo_numero = 1  # Reiniciar el número de factura
                cursor.execute("UPDATE configuracion SET ultimo_numero = %s, año = %s", (nuevo_numero, current_year))
            else:
                nuevo_numero = ultimo_numero + 1
                cursor.execute("UPDATE configuracion SET ultimo_numero = %s WHERE año = %s", (nuevo_numero, año))
        else:
            nuevo_numero = 1
            cursor.execute("INSERT INTO configuracion (ultimo_numero, año) VALUES (1, YEAR(CURRENT_DATE))")

        db.commit()
        db.close()
        return nuevo_numero

    def cargar_clientes(self):
        tipo = self.tipo_cliente.get()
        db = conectar_db()
        cursor = db.cursor()
        if tipo == "socis":
            cursor.execute("SELECT id, nom FROM socis")
        else:
            cursor.execute("SELECT id, nom FROM esporadics")

        clientes = cursor.fetchall()
        self.combo_clientes['values'] = [cliente[1] for cliente in clientes]
        self.combo_clientes.selected_id = [cliente[0] for cliente in clientes]  # Guardar IDs
        db.close()

    def buscar_cliente(self):
        texto_busqueda = self.combo_clientes.get()
        if texto_busqueda:
            tipo = self.tipo_cliente.get()
            db = conectar_db()
            cursor = db.cursor()
            if tipo == "socis":
                cursor.execute("SELECT id, nom FROM socis WHERE nom LIKE %s", (f"%{texto_busqueda}%",))
            else:
                cursor.execute("SELECT id, nom FROM esporadics WHERE nom LIKE %s", (f"%{texto_busqueda}%",))

            clientes = cursor.fetchall()
            self.combo_clientes['values'] = [cliente[1] for cliente in clientes]
            self.combo_clientes.selected_id = [cliente[0] for cliente in clientes]  # Guardar IDs
            db.close()
        else:
            self.cargar_clientes()

    def cargar_detalle_cliente(self, event):
        db = conectar_db()
        cursor = db.cursor()
        selected_index = self.combo_clientes.current()
        if selected_index == -1:
            return  # No hay cliente seleccionado

        client_id = self.combo_clientes.selected_id[selected_index]
        cursor.execute("SELECT activitats, Quantitat FROM socis WHERE id = %s", (client_id,))
        result = cursor.fetchone()

        if result:
            activitats, cantidad_con_iva = result
            activitats = activitats or ""
            self.actividades_text.delete("1.0", END)
            self.actividades_text.insert("1.0", activitats)

            # Convertir `cantidad_con_iva` a float antes de realizar cálculos
            cantidad_con_iva = float(cantidad_con_iva)
            iva = float(self.iva_entry.get())
            cantidad_sin_iva = cantidad_con_iva / (1 + (iva / 100))  # Calcular sin IVA
            self.cantidad_sin_iva.set(f"{cantidad_sin_iva:.2f}")
            self.iva_calculado.set(f"{cantidad_con_iva - cantidad_sin_iva:.2f}")
            self.total_con_iva.set(f"{cantidad_con_iva:.2f}")
        db.close()

    def generar_pdf(self, numero_factura, fecha_factura, actividades, cantidad_sin_iva, iva, total_con_iva):
        filename = f"factura_{numero_factura}.pdf"
        c = canvas.Canvas(filename, pagesize=letter)
        c.drawString(100, 750, f"Factura: {numero_factura}")
        c.drawString(100, 735, f"Fecha: {fecha_factura}")
        c.drawString(100, 720, f"Actividades: {actividades}")
        c.drawString(100, 705, f"Cantidad (Sin IVA): {cantidad_sin_iva}")
        c.drawString(100, 690, f"IVA (%): {iva}")
        c.drawString(100, 675, f"Total con IVA: {total_con_iva}")
        c.save()

    def guardar_factura(self):
 
        actividades = self.actividades_text.get("1.0", END).strip()
        cantidad_sin_iva = Decimal(self.cantidad_sin_iva.get())
        iva = Decimal(self.iva_entry.get())
        total_con_iva = cantidad_sin_iva * (1 + iva / 100)
        numero_factura = self.numero_factura
        fecha_factura = self.fecha_entry.get_date().strftime("%d-%m-%Y")

        # Guardar en la base de datos
        db = conectar_db()
        cursor = db.cursor()
        cursor.execute("INSERT INTO facturas (numero_factura, fecha, actividades, cantidad, iva, total) VALUES (%s, %s, %s, %s, %s, %s)",
                       (numero_factura, fecha_factura, actividades, cantidad_sin_iva, iva, total_con_iva))
        db.commit()

        # Generar y guardar el PDF
        self.generar_pdf(numero_factura, fecha_factura, actividades, cantidad_sin_iva, iva, total_con_iva)

        # Actualizar el número de factura
        self.numero_factura = self.obtener_numero_factura()

        # Actualizar el campo de entrada del número de factura
        self.numero_factura_entry.delete(0, END)  # Limpiar el campo
        self.numero_factura_entry.insert(0, str(self.numero_factura))  # Insertar el nuevo número

        # Preguntar al usuario si desea ver la factura
        respuesta = messagebox.askyesno("Ver Factura", "¿Desea ver la factura en pantalla?")
        if respuesta:
            # Ejecutar el script plantilla.py
            subprocess.run(["python", "plantilla.py", str(numero_factura)])  # Asegúrate de que la ruta sea correcta

        messagebox.showinfo("Factura Guardada", f"Factura #{numero_factura} guardada correctamente.")
        db.close()

# Crear y ejecutar la aplicación
root = Tk()
app = FacturacionApp(root)
root.mainloop()