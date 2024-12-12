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

# Crear la tabla 'facturas' si no existe
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
            dia_proxima_factura DATE NOT NULL
        )
    """)
    print("Tabla 'facturas' creada/verificada correctamente.")
    cursor.close()
    conn.close()

# Obtener el último número de factura del año actual
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
        return int(result[0].split('-')[1])  # Extrae el número después del guion
    return 0

# Obtener la última fecha de factura de un cliente
def obtener_fecha_ultima_factura(cliente_id):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT MAX(fecha) FROM facturas WHERE cliente_id = %s
    """, (cliente_id,))
    result = cursor.fetchone()[0]
    cursor.close()
    conn.close()
    return result

# Generar facturas pendientes para los socios
def facturar_socis():
    conn = connect_db()
    cursor = conn.cursor(dictionary=True)
    last_invoice_number = get_last_invoice_number()
    hoy = datetime.now().date()

    # Verificar que solo se facturen a partir del mes actual (primer día del mes)
    primer_dia_mes_actual = datetime(hoy.year, hoy.month, 1).date()

    if hoy < primer_dia_mes_actual:
        print("No se generarán facturas antes del primer día del mes actual.")
        return  # Salir si hoy es antes del primer día del mes actual

    # Obtener socios activos
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

        # Convertir 'alta' a fecha si no es None
        if alta is None:
            print(f"Error: La fecha de alta de {nom} es None.")
            continue  # Saltar este socio si no tiene fecha de alta válida

        if isinstance(alta, str):
            alta = datetime.strptime(alta, '%Y-%m-%d').date()  # Convertir a datetime.date si es string

        # Determinar la fecha de inicio para facturación
        fecha_ultima_factura = obtener_fecha_ultima_factura(cliente_id)
        
        # Si no existe fecha de última factura, usar la fecha de alta
        if fecha_ultima_factura is None:
            fecha_actual = alta
        else:
            fecha_actual = fecha_ultima_factura

        # Verificar que la fecha_actual esté en el mes actual o posterior
        if fecha_actual < primer_dia_mes_actual:
            fecha_actual = primer_dia_mes_actual  # Si la última factura fue antes del mes actual, empezamos desde el primer día de este mes

        # Recorrer desde la última factura hasta hoy, en intervalos de 30 días
        while fecha_actual <= hoy:
            if fecha_actual != fecha_ultima_factura:  # Evitar repetir la última factura existente
                # Calcular desglose de precios
                iva = round(quantitat * 0.21, 2)
                preu = round(quantitat - iva, 2)
                total = quantitat
                last_invoice_number += 1
                numero_factura = f"{hoy.year}-{last_invoice_number:03d}"

                # Corregir la fecha de la próxima factura (asegurarse de que no sea antes de hoy)
                dia_proxima_factura = max(fecha_actual + timedelta(days=30), hoy)

                # Insertar la factura en la base de datos
                cursor.execute("""
                    INSERT INTO facturas (cliente_id, tipo_cliente, activitats, Preu, iva, total, impuesto, fecha, numero_factura, dia_proxima_factura)
                    VALUES (%s, 'socis', %s, %s, %s, %s, %s, %s, %s, %s)
                """, (cliente_id, activitats, preu, iva, total, iva, fecha_actual, numero_factura, dia_proxima_factura))
                print(f"Factura generada para {nom}: {numero_factura}, Fecha: {fecha_actual}, Proxima factura: {dia_proxima_factura}")

            # Sumar 30 días para la próxima factura
            fecha_actual += timedelta(days=30)

    conn.commit()
    cursor.close()
    conn.close()

# Ejecutar el script
if __name__ == "__main__":
    crear_tabla_facturas()
    facturar_socis()
