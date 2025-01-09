import mysql.connector
from fpdf import FPDF
import os
import qrcode
from datetime import datetime
import configparser

# Leer configuración desde config.ini
def obtener_config():
    config = configparser.ConfigParser()
    config.read("config.ini")
    return config["mysql"]

# Conexión a la base de datos
def obtener_datos_factura(numero_factura):
    try:
        config = obtener_config()
        conexion = mysql.connector.connect(
            host=config["host"],
            user=config["user"],
            password=config["password"],
            database=config["database"]
        )
        cursor = conexion.cursor(dictionary=True)
        
        # Ajusta 'numero_factura' por el nombre correcto de la columna
        cursor.execute("SELECT * FROM facturas WHERE numero_factura = %s", (numero_factura,))
        factura = cursor.fetchone()
        
        if not factura:
            print("Factura no encontrada.")
            exit()

        # Consulta de la tabla 'empresa'
        cursor.execute("SELECT * FROM empresa WHERE id = 1")
        empresa = cursor.fetchone()

        cursor.close()
        conexion.close()

        return factura, empresa

    except mysql.connector.Error as err:
        print(f"Error: {err}")
        exit()

# Generar código QR
def generar_qr(url, qr_path):
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(url)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")
    img.save(qr_path)

# Generar PDF de la factura
def generar_pdf_factura(numero_factura):
    factura, empresa = obtener_datos_factura(numero_factura)

    # Crear objeto PDF
    pdf = FPDF()
    pdf.add_page()
    pdf.add_font('DejaVu', '', 'C:\\Windows\\Fonts\\arial.ttf', uni=True)  # Fuente estándar
    pdf.set_font("DejaVu", size=10)

    # Directorio donde se encuentra el script
    script_dir = os.path.dirname(__file__)  # Obtiene el directorio donde está el script

    # Ruta relativa para el logo, buscando dentro de la estructura del proyecto
    logo_path = os.path.join(script_dir, "..", "logo", "logo.jpg")  # Busca en la carpeta logo al nivel superior
    qr_path = os.path.join(script_dir, "qr_temp.png")  # Ruta para el archivo QR en el mismo directorio del script
    pdf_path = f"factura_{numero_factura}.pdf"  # Ruta para el PDF generado en el directorio del script

    # Generar QR
    generar_qr(empresa['pagina_web'], qr_path)

    # Logo de la empresa
    pdf.image(logo_path, x=150, y=10, w=40)  # A la derecha
    pdf.image(qr_path, x=10, y=10, w=40)    # QR a la izquierda

    # Datos de la empresa
    pdf.set_xy(10, 55)
    pdf.cell(0, 10, f"{empresa['nom']}", ln=True)
    pdf.cell(0, 10, f"Dirección: {empresa['adresa']}, {empresa['poblacio']}, {empresa['provincia']}", ln=True)
    pdf.cell(0, 10, f"Código Postal: {empresa['codi_postal']}", ln=True)
    pdf.cell(0, 10, f"Teléfono: {empresa['telefon']} | Móvil: {empresa['mobil']}", ln=True)
    pdf.cell(0, 10, f"Email: {empresa['email']} | CIF/NIF: {empresa['cif_nif']}", ln=True)

    # Espacio
    pdf.ln(10)

    # Datos de la factura
    pdf.set_font("DejaVu", size=12)
    pdf.cell(0, 10, f"Factura Número: {factura['numero_factura']}", ln=True)
    pdf.cell(0, 10, f"Fecha: {factura['fecha']}", ln=True)
    pdf.cell(0, 10, f"Cliente: {factura['client_nom']}", ln=True)

    # Línea divisoria
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(10)

    # Descripción de la factura
    pdf.set_font("DejaVu", size=10)
    pdf.cell(0, 10, "Detalle de la Factura:", ln=True)
    pdf.multi_cell(0, 10, factura['activitats'])  # Campo de descripción

    # Espacio y total
    pdf.ln(5)
    pdf.cell(0, 10, f"Subtotal: {factura['preu']} €", ln=True)
    pdf.cell(0, 10, f"IVA (21%): {factura['iva']} €", ln=True)
    pdf.cell(0, 10, f"Total: {factura['total']} €", ln=True)

    # Guardar PDF
    pdf.output(pdf_path)
    print(f"Factura generada: {pdf_path}")

    # Abrir PDF automáticamente
    os.startfile(pdf_path)

    # Eliminar QR temporal
    os.remove(qr_path)

# Programa principal
if __name__ == "__main__":
    numero_factura = input("Ingrese el número de la factura: ")
    generar_pdf_factura(numero_factura)
