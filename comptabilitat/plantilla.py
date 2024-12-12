import qrcode
import mysql.connector
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

def generar_qr(pagina_web, output_path):
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(pagina_web)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    img.save(output_path)

def crear_pdf(logo_path, datos_empresa):
    # Generar QR
    qr_path = "qr_code.png"
    generar_qr(datos_empresa['pagina_web'], qr_path)

    # Crear PDF
    c = canvas.Canvas("factura_empresa.pdf", pagesize=letter)

    # Definir márgenes
    margen_izquierdo = 50
    margen_derecho = 50
    margen_superior = 70.87  # 2.5 cm en puntos
    margen_inferior = 50

    # Cargar logo y QR
    c.drawImage(logo_path, 450 - margen_derecho, 700 - margen_superior, width=100, height=100)  # Logo
    c.drawImage(qr_path, margen_izquierdo, 700 - margen_superior, width=100, height=100)  # QR

    # Añadir datos de la empresa
    y_position = 700 - margen_superior
    c.drawString(margen_izquierdo, y_position, f"Nom: {datos_empresa['nom']}")
    c.drawString(margen_izquierdo, y_position - 15, f"Adresa: {datos_empresa['adresa']}")
    
    # Població y Provincia en la misma línea
    c.drawString(margen_izquierdo, y_position - 30, f"Població: {datos_empresa['poblacio']} - Provincia: {datos_empresa['provincia']}")
    
    c.drawString(margen_izquierdo, y_position - 45, f"Códi Postal: {datos_empresa['codi_postal']}")
    c.drawString(margen_izquierdo, y_position - 60, f"Telefon: {datos_empresa['telefon']}")
    
    # Añadir el campo móvil
    c.drawString(margen_izquierdo, y_position - 75, f"Mòbil: {datos_empresa['mobil']}")
    
    c.drawString(margen_izquierdo, y_position - 90, f"Email: {datos_empresa['email']}")

    # Finalizar el PDF
    c.save()
    print("PDF generado: factura_empresa.pdf")

def obtener_datos_empresa():
    # Conectar a la base de datos MySQL
    conexion = mysql.connector.connect(
        host='localhost',
        user='root',
        password='',
        database='gimnas'
    )
    cursor = conexion.cursor(dictionary=True)
    cursor.execute("SELECT nom, adresa, poblacio, provincia, codi_postal, telefon, mobil, email, pagina_web FROM empresa WHERE id = 1")
    datos_empresa = cursor.fetchone()
    cursor.close()
    conexion.close()
    return datos_empresa

if __name__ == "__main__":
    logo_path = "logo/logo.jpg"  # Ruta del logo
    datos_empresa = obtener_datos_empresa()
    crear_pdf(logo_path, datos_empresa)