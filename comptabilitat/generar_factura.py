import mysql.connector
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm
from reportlab.lib.utils import ImageReader
import qrcode
from reportlab.platypus import Table, TableStyle
import os  # Importa el módulo os para abrir el archivo PDF

# Configuración de la conexión a la base de datos
def conectar_bd():
    """Conecta a la base de datos MySQL."""
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="",  # Ajusta si tu usuario tiene contraseña
        database="gimnas"  # Nombre de la base de datos
    )

def obtener_datos_empresa():
    """Obtiene los datos de la tabla 'empresa'."""
    conexion = conectar_bd()
    cursor = conexion.cursor(dictionary=True)
    cursor.execute("SELECT nom, adresa, poblacio, provincia, codi_postal, telefon, mobil, email, pagina_web, cif_nif FROM empresa LIMIT 1")
    datos = cursor.fetchone()
    cursor.close()
    conexion.close()
    return datos

def obtener_datos_cliente(cliente_id):
    """Obtiene los datos de un cliente desde la base de datos."""
    conexion = conectar_bd()
    cursor = conexion.cursor(dictionary=True)
    cursor.execute("""
        SELECT * FROM socis WHERE ID = %s
        """, (cliente_id,))
    datos = cursor.fetchone()
    cursor.close()
    conexion.close()
    return datos

def obtener_datos_factura(numero_factura):
    """Obtiene los detalles de la factura desde la base de datos."""
    conexion = conectar_bd()
    cursor = conexion.cursor(dictionary=True)
    cursor.execute("""
        SELECT activitats, preu, iva, total FROM facturas WHERE numero_factura = %s
        """, (numero_factura,))
    datos = cursor.fetchone()
    cursor.close()
    conexion.close()
    return datos

def generar_qr(pagina_web):
    """Genera un código QR con la URL de la página web."""
    qr = qrcode.make(pagina_web)
    qr.save("qr_temp.png")
    return "qr_temp.png"

def generar_pdf(numero_factura, cliente_id):
    """Genera el PDF de la factura con los datos de la empresa y el cliente."""
    # Tamaño de la página
    ancho_pagina, alto_pagina = A4
    margen = 2 * cm  # Márgenes

    # Obtener el directorio de Descargas
    directorio_descargas = os.path.join(os.environ["USERPROFILE"], "Downloads")
    if not os.path.exists(directorio_descargas):
        print("La carpeta Descargas no se encuentra en el perfil de usuario.")
        return

    # Crear nombre de archivo y la ruta completa
    nombre_archivo = f"factura_{numero_factura}.pdf"
    ruta_archivo = os.path.join(directorio_descargas, nombre_archivo)

    # Crear PDF
    c = canvas.Canvas(ruta_archivo, pagesize=A4)

    # Obtener los datos de la empresa
    datos_empresa = obtener_datos_empresa()

    # Obtener los datos del cliente
    datos_cliente = obtener_datos_cliente(cliente_id)

    # Obtener los datos de la factura
    datos_factura = obtener_datos_factura(numero_factura)

    # Posiciones iniciales
    qr_path = generar_qr(datos_empresa['pagina_web'])  # Generar QR con la página web de la empresa
    logo_path = "c:/dinamic/logo/logo.jpg"  # Ruta ajustada del logo

    # Dibujar Logo
    try:
        logo = ImageReader(logo_path)
        c.drawImage(logo, ancho_pagina - margen - 4 * cm, alto_pagina - margen - 4 * cm, width=4 * cm, height=4 * cm)
    except Exception as e:
        print(f"Error cargando el logo: {e}")

    # Dibujar QR
    try:
        qr = ImageReader(qr_path)
        c.drawImage(qr, margen, alto_pagina - margen - 4 * cm, width=3 * cm, height=3 * cm)
    except Exception as e:
        print(f"Error cargando el QR: {e}")

    # Número de factura
    c.setFont("Helvetica-Bold", 12)
    y_numero_factura = alto_pagina - margen - 5 * cm
    c.drawString(margen, y_numero_factura, f"Número de factura: {numero_factura}")

    # Datos de la empresa
    c.setFont("Helvetica", 10)
    datos_empresa_text = [
        f"{datos_empresa['nom']} | CIF/NIF: {datos_empresa['cif_nif']}",
        f"Adreça: {datos_empresa['adresa']}",
        f"Població: {datos_empresa['poblacio']}",
        f"Província: {datos_empresa['provincia']}",
        f"Codi Postal: {datos_empresa['codi_postal']}",
        f"Telèfon: {datos_empresa['telefon']} | Mòbil: {datos_empresa['mobil']}",
        f"Email: {datos_empresa['email']}"
    ]

    # Calcular ancho dinámico del recuadro
    ancho_texto = max(c.stringWidth(linea, "Helvetica", 10) for linea in datos_empresa_text)
    ancho_recuadro = ancho_texto + 1 * cm  # Añadir margen horizontal
    altura_linea = 0.5 * cm
    altura_recuadro = len(datos_empresa_text) * altura_linea + 1 * cm  # Extra espacio superior e inferior

    # Posición del recuadro (justo debajo del número de factura)
    x_recuadro = margen
    y_recuadro = y_numero_factura - altura_recuadro - 1 * cm  # 1 cm de separación

    # Dibujar el recuadro de la empresa
    c.rect(x_recuadro, y_recuadro, ancho_recuadro, altura_recuadro)

    # Escribir los datos de la empresa dentro del recuadro
    y_texto = y_recuadro + altura_recuadro - 0.8 * cm  # Ajuste para la posición inicial del texto
    for linea in datos_empresa_text:
        c.drawString(x_recuadro + 0.5 * cm, y_texto, linea)
        y_texto -= altura_linea  # Bajar a la siguiente línea

    # Datos del cliente (a la derecha)
    c.setFont("Helvetica", 10)
    datos_cliente_text = [
        f"DNI: {datos_cliente['DNI']}",
        f"Nom: {datos_cliente['Nom']}",
        f"Carrer: {datos_cliente['Carrer']} | Codi Postal: {datos_cliente['Codipostal']}",
        f"Població: {datos_cliente['Poblacio']}",
        f"Província: {datos_cliente['Provincia']}",
        f"Email: {datos_cliente['email']}",
        f"Telèfon 1: {datos_cliente['Telefon1']}",
    ]

    # Calcular ancho dinámico del recuadro del cliente
    ancho_texto_cliente = max(c.stringWidth(linea, "Helvetica", 10) for linea in datos_cliente_text)
    ancho_recuadro_cliente = ancho_texto_cliente + 1 * cm
    altura_recuadro_cliente = len(datos_cliente_text) * altura_linea + 1 * cm  # Extra espacio

    # Posición del recuadro del cliente (a la derecha)
    x_recuadro_cliente = x_recuadro + ancho_recuadro + 2 * cm  # 2 cm de separación entre recuadros
    y_recuadro_cliente = y_recuadro

    # Dibujar el recuadro de los datos del cliente
    c.rect(x_recuadro_cliente, y_recuadro_cliente, ancho_recuadro_cliente, altura_recuadro_cliente)

    # Escribir los datos del cliente dentro del recuadro
    y_texto_cliente = y_recuadro_cliente + altura_recuadro_cliente - 0.8 * cm
    for linea in datos_cliente_text:
        c.drawString(x_recuadro_cliente + 0.5 * cm, y_texto_cliente, linea)
        y_texto_cliente -= altura_linea  # Bajar a la siguiente línea

    # Detalles de las activitats y tabla
    c.setFont("Helvetica-Bold", 10)
    y_activitats = y_texto_cliente - 1 * cm
    c.drawString(margen, y_activitats, "")

    # Crear tabla de activitats
    data = [["Descripció", "Preu (€)", "IVA (%)", "Total (€)"]]
    activitats = datos_factura['activitats'].split(',')  # Supone que las activitats están separadas por comas
    preu = datos_factura['preu']
    iva = datos_factura['iva']
    total = datos_factura['total']
    
    # Si solo hay una actividad, mostrarla en una sola línea
    if len(activitats) == 1:
        data.append([activitats[0], f"{preu}€", f"{iva}%", f"{total}€"])
    else:
        # En caso de más de una actividad, concatenarlas en una línea
        actividades_concatenadas = ', '.join(activitats)
        data.append([actividades_concatenadas, f"{preu}€", f"{iva}%", f"{total}€"])

    # Crear la tabla
    table = Table(data, colWidths=[8 * cm, 3 * cm, 2 * cm, 3 * cm])
    table.setStyle(TableStyle([
        ('TEXTCOLOR', (0, 0), (-1, 0), (0, 0, 0)),  # Cabecera en color negro
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('GRID', (0, 0), (-1, -1), 0.5, (0, 0, 0)),  # Cuadrícula
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
    ]))

    # Dibujar la tabla en el PDF
    table.wrapOn(c, ancho_pagina, alto_pagina)
    table.drawOn(c, margen, y_activitats - 2 * cm)  # Ajuste para dibujar la tabla

    # Guardar el PDF
    c.save()

    # Abrir el PDF automáticamente
    os.startfile(ruta_archivo)  # Esto abrirá el archivo en el visor predeterminado del sistema

    print(f"Factura generada y abierta: {ruta_archivo}")

# Ejecución principal
if __name__ == "__main__":
    import sys
    # Verifica si se pasa un número de factura como argumento
    if len(sys.argv) > 1:
        numero_factura = sys.argv[1]
    else:
        numero_factura = "2024-001"  # Número de factura predeterminado para pruebas

    # Verifica si se pasa un ID de cliente
    if len(sys.argv) > 2:
        cliente_id = sys.argv[2]
    else:
        cliente_id = 1  # Cliente de prueba

    generar_pdf(numero_factura, cliente_id)
