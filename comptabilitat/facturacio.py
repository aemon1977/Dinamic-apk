import mysql.connector
from datetime import datetime, timedelta

# Conexión a la base de datos
def connect_db():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="gimnas"
    )

# Crear la tabla 'facturas' si no existe y agregar la columna 'dia_proxima_factura'
def crear_tabla_facturas():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS facturas (
            id INT AUTO_INCREMENT PRIMARY KEY,
            cliente_id INT NOT NULL,
            tipo_cliente VARCHAR(20) NOT NULL,
            activitats TEXT,
            Preu DECIMAL(10,2),
            iva DECIMAL(10,2),
            total DECIMAL(10,2),
            impuesto DECIMAL(10,2),
            fecha DATE NOT NULL,
            numero_factura VARCHAR(20) NOT NULL,
            dia_proxima_factura DATE NOT NULL  -- Nueva columna para la próxima factura
        )
    """)
    print("Tabla 'facturas' verificada o creada correctamente.")
    cursor.close()
    conn.close()

# Obtener el último número de factura por año
def get_last_invoice_number():
    conn = connect_db()
    cursor = conn.cursor()
    current_year = datetime.now().year
    cursor.execute("""
        SELECT MAX(numero_factura) 
        FROM facturas 
        WHERE YEAR(fecha) = %s
    """, (current_year,))
    result = cursor.fetchone()
    cursor.close()
    conn.close()
    if result[0]:
        last_invoice = result[0]
        return int(last_invoice.split('-')[1])  # Obtener el número sin el año
    return 0

# Obtener la fecha de la última factura
def obtener_fecha_ultima_factura(cliente_id):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT MAX(fecha) 
        FROM facturas 
        WHERE cliente_id = %s
    """, (cliente_id,))
    result = cursor.fetchone()[0]
    cursor.close()
    conn.close()
    return result  # Si no hay factura, devuelve None

# Verificar si el socio ya ha sido facturado este mes
def ya_facturado_mes(cliente_id, tipo_cliente, mes, anio):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT COUNT(*) FROM facturas
        WHERE cliente_id = %s AND tipo_cliente = %s
        AND MONTH(fecha) = %s AND YEAR(fecha) = %s
    """, (cliente_id, tipo_cliente, mes, anio))
    result = cursor.fetchone()[0]
    cursor.close()
    conn.close()
    return result > 0

# Generar factura automáticamente
def facturar_socis():
    conn = connect_db()
    cursor = conn.cursor(dictionary=True)
    last_invoice_number = get_last_invoice_number()
    hoy = datetime.now().date()
    current_year = hoy.year
    primer_dia_mes = hoy.replace(day=1)  # Primer día del mes actual

    # Seleccionar los socios con actividades y sin baja definitiva
    cursor.execute("""
        SELECT ID, Nom, Activitats, Quantitat, Alta, Baixa
        FROM socis
        WHERE Activitats IS NOT NULL AND Activitats != ''
    """)
    socis = cursor.fetchall()

    for socio in socis:
        cliente_id = socio['ID']
        nom = socio['Nom']
        activitats = socio['Activitats']
        quantitat = float(socio['Quantitat'])
        alta = socio['Alta']
        baixa = socio['Baixa']

        # Obtener la fecha de la última factura
        fecha_ultima_factura = obtener_fecha_ultima_factura(cliente_id)

        # Si no hay una factura previa, usar la fecha de alta del socio
        if fecha_ultima_factura is None:
            # Si no existe fecha de factura previa, asignamos la fecha de alta para la primera factura
            fecha_ultima_factura = alta
            print(f"No se encontró factura previa para {nom}, usando la fecha de alta {alta} como referencia.")
        
        # Verificar si fecha_ultima_factura tiene valor
        if fecha_ultima_factura is None:
            print(f"No se puede calcular la fecha de la próxima factura para {nom} porque la fecha de la última factura es None.")
            continue

        # Calcular la diferencia en días entre el primer día de este mes y la fecha de alta
        dias_diferencia = (primer_dia_mes - alta).days
        
        # Verificar si la diferencia de días es un múltiplo de 30
        if dias_diferencia % 30 == 0:
            # Generar factura solo si es un múltiplo de 30 desde el primer día del mes
            # Calcular la fecha de la próxima factura
            fecha_proxima_factura = hoy

            # Verificar si ya fue facturado este mes
            if ya_facturado_mes(cliente_id, 'socis', fecha_proxima_factura.month, fecha_proxima_factura.year):
                print(f"El socio {nom} ya fue facturado en el mes de {fecha_proxima_factura.strftime('%Y-%m')}.")
                continue

            # Calcular desglose de precios
            iva = round(quantitat * 0.21, 2)
            preu = round(quantitat - iva, 2)
            total = quantitat
            last_invoice_number += 1
            numero_factura = f"{current_year}-{last_invoice_number:03d}"  # Formato de factura

            # Insertar la factura con la fecha de la próxima factura
            cursor.execute("""
                INSERT INTO facturas (cliente_id, tipo_cliente, activitats, Preu, iva, total, impuesto, fecha, numero_factura, dia_proxima_factura)
                VALUES (%s, 'socis', %s, %s, %s, %s, %s, %s, %s, %s)
            """, (cliente_id, activitats, preu, iva, total, iva, fecha_proxima_factura, numero_factura, fecha_proxima_factura))

            print(f"Factura generada para {nom} - Número de factura: {numero_factura} - Próxima factura el {fecha_proxima_factura}")

    conn.commit()
    cursor.close()
    conn.close()

# Ejecutar el script
if __name__ == "__main__":
    crear_tabla_facturas()  # Verificar y crear la tabla si no existe
    facturar_socis()        # Generar facturas automáticamente
