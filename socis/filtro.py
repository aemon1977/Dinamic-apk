import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from tkcalendar import DateEntry  # Importar DateEntry de tkcalendar
import mysql.connector
from PIL import Image, ImageFile, ImageTk
import io
import configparser
from datetime import datetime

def format_date(date_str):
    if date_str and date_str != 'None':  # Asegúrate de que no sea 'None'
        date_obj = datetime.strptime(date_str, '%Y-%m-%d')  # Convertir a objeto datetime
        return date_obj.strftime('%d-%m-%Y')  # Formatear a dd-mm-yyyy
    return ""  # Retornar vacío si date_str es None o 'None'

# Permitir la carga de imágenes truncadas
ImageFile.LOAD_TRUNCATED_IMAGES = True

# Leer la configuración de la base de datos desde config.ini
config = configparser.ConfigParser()
config.read('config.ini')

# Configuración de la base de datos
def conectar_db():
    return mysql.connector.connect(
        host=config['mysql']['host'],
        user=config['mysql']['user'],
        password=config['mysql']['password'],
        database=config['mysql']['database']
    )

# Función para cargar datos de la base de datos
def cargar_datos(busqueda=None, orden_columna='Data_modificacio', orden='DESC'):
    conn = conectar_db()
    cursor = conn.cursor(dictionary=True)

    query = """SELECT ID, DNI, Nom, Carrer, Codipostal, Poblacio, Provincia, email, 
                Data_naixement, Telefon1, Telefon2, Telefon3, Numero_Conta, Sepa, 
                Activitats, Quantitat, Alta, Baixa, Facial, Data_Inici_activitat, 
                En_ma, Data_modificacio, usuari FROM socis"""
    if busqueda:
        query += " WHERE Nom LIKE %s OR DNI LIKE %s OR Activitats LIKE %s"
        cursor.execute(query + f" ORDER BY {orden_columna} {orden}", 
                       ('%' + busqueda + '%', '%' + busqueda + '%', '%' + busqueda + '%'))
    else:
        query += f" ORDER BY {orden_columna} {orden}"
        cursor.execute(query)

    rows = cursor.fetchall()
    conn.close()
    return rows

# Función para mostrar los datos en el Treeview
def mostrar_datos(busqueda=None, orden_columna='Data_modificacio', orden='DESC'):
    for row in tree.get_children():
        tree.delete(row)

    for row in cargar_datos(busqueda, orden_columna, orden):
        tree.insert('', 'end', values=(
            row['ID'], row['DNI'], row['Nom'], row['Carrer'], row['Codipostal'],
            row['Poblacio'], row['Provincia'], row['email'], row['Data_naixement'],
            row['Telefon1'], row['Telefon2'], row['Telefon3'], row['Numero_Conta'],
            row['Sepa'], row['Activitats'], row['Quantitat'], row['Alta'], row['Baixa'],
            row['Facial'], row['Data_Inici_activitat'], row['En_ma'], row['Data_modificacio'], row['usuari']
        ))

# Variable global para almacenar el orden de cada columna
ordenes_columnas = {col: 'DESC' for col in ["Data_modificacio", "DNI", "Nom", "Carrer", 
                                             "Codipostal", "Poblacio", "Provincia", 
                                             "Email", "Data_naixement", "Telefon1", 
                                             "Telefon2", "Telefon3", "Numero_Conta", 
                                             "Sepa", "Activitats", "Quantitat", "Alta", 
                                             "Baixa", "Facial", "Data_Inici_activitat", 
                                             "En_ma"]}

# Función para ordenar la tabla
def ordenar_tabla(columna):
    if columna in ordenes_columnas:
        ordenes_columnas[columna] = 'ASC' if ordenes_columnas[columna] == 'DESC' else 'DESC'
    mostrar_datos(orden_columna=columna, orden=ordenes_columnas[columna])

# Función para eliminar el registro seleccionado
def eliminar_registro():
    selected_item = tree.selection()
    if selected_item:
        item = tree.item(selected_item)
        id_socio = item['values'][0]

        respuesta = messagebox.askyesno("Confirmar", "Estàs segur que vols eliminar aquest registre?")
        if respuesta:
            try:
                conn = conectar_db()
                cursor = conn.cursor()
                cursor.execute("DELETE FROM socis WHERE ID = %s", (id_socio,))
                conn.commit()
                conn.close()

                messagebox.showinfo("Èxit", "Registre eliminat correctament.")
                mostrar_datos()
            except mysql.connector.Error as e:
                messagebox.showerror("Error", f"Error en eliminar el registre: {e}")
        else:
            messagebox.showinfo("Cancel·lat", "L'eliminació ha estat cancel·lada.")
    else:
        messagebox.showwarning("Selecció", "Si us plau, selecciona un registre per eliminar.")

# Función para buscar
def buscar(event=None):  # Permitir que se llame sin argumentos
    busqueda = entrada_busqueda.get()
    mostrar_datos(busqueda)

# Función para cargar datos en el formulario
def cargar_en_formulario(event):
    selected_item = tree.selection()
    if selected_item:
        item = tree.item(selected_item)
        datos = item['values']
        
        entrada_dni.delete(0, tk.END)
        entrada_dni.insert(0, datos[1])

        entrada_nom.delete(0 , tk.END)
        entrada_nom.insert(0, datos[2])

        entrada_carrer.delete(0, tk.END)
        entrada_carrer.insert(0, datos[3])

        entrada_codipostal.delete(0, tk.END)
        entrada_codipostal.insert(0, datos[4])

        entrada_poblacio.delete(0, tk.END)
        entrada_poblacio.insert(0, datos[5])

        entrada_provincia.delete(0, tk.END)
        entrada_provincia.insert(0, datos[6])

        entrada_email.delete(0, tk.END)
        entrada_email.insert(0, datos[7])

        # Modificar aquí para usar format_date
        entrada_data_naixement.delete(0, tk.END)
        entrada_data_naixement.insert(0, format_date(datos[8]))  # Fecha de nacimiento

        entrada_telefon1.delete(0, tk.END)
        entrada_telefon1.insert(0, datos[9])  # Teléfono 1

        entrada_telefon2.delete(0, tk.END)
        entrada_telefon2.insert(0, datos[10])  # Teléfono 2

        entrada_telefon3.delete(0, tk.END)
        entrada_telefon3.insert(0, datos[11])  # Teléfono 3

        entrada_numero_conta.delete(0, tk.END)
        entrada_numero_conta.insert(0, datos[12])  # Número de cuenta

        var_sepa.set(datos[13] == 1)  # SEPA
        var_facial.set(datos[18] == 1)  # Facial
        var_en_ma.set(datos[19] == 1)  # En ma

        # Clear previous activity selections
        checked_listbox.selection_clear(0, tk.END)  # Limpiar todas las selecciones

        # Load activities for the selected member
        actividades = cargar_activitats(datos[0])

        for i in range(checked_listbox.size()):
            actividad_nombre = checked_listbox.get(i)
            if actividad_nombre.strip() in actividades:
                checked_listbox.selection_set(i)  # Volver a seleccionar las actividades

        entrada_quantitat.delete(0, tk.END)
        entrada_quantitat.insert(0, datos[15])  # Quantitat
        
        entrada_data_alta.delete(0, tk.END)
        entrada_data_alta.insert(0, format_date(datos[16]))  # Data d'Alta

        entrada_data_baixa.delete(0, tk.END)
        # Solo formatear si datos[17] no es None
        if datos[17] is not None:
            entrada_data_baixa.insert(0, format_date(datos[17]))  # Data de Baixa
        else:
            entrada_data_baixa.insert(0, "")  # Dejar vacío si no hay fecha

        entrada_data_inici_activitat.delete(0, tk.END)
        entrada_data_inici_activitat.insert(0, format_date(datos[19]))  # Data d'Inici Activitat

        entrada_usuari.delete(0, tk.END)
        entrada_usuari.insert(0, datos[22])  # Usuari

        cargar_foto(datos[0])  # ID del socio seleccionado
        
# Función para cargar actividades
def cargar_activitats(id_socio):
    # Retrieve activities for the specified member from the database
    conn = conectar_db()
    cursor = conn.cursor()
    cursor.execute("SELECT Activitats FROM socis WHERE ID = %s", (id_socio,))
    actividades = cursor.fetchone()
    conn.close()

    if actividades and actividades[0]:
        return actividades[0].split(",")
    else:
        return []

# Crear una imagen en blanco para mostrar cuando no hay foto
def crear_imagen_blanco():
    imagen_blanco = Image.new("RGB", (100, 130), (255, 255, 255))  # Color blanco
    return ImageTk.PhotoImage(imagen_blanco)

# Función para cargar la foto
def cargar_foto(id_socio):
    try:
        conn = conectar_db()
        cursor = conn.cursor()
        cursor.execute("SELECT Foto FROM socis WHERE ID = %s", (id_socio,))
        foto_blob = cursor.fetchone()
        conn.close()

        if foto_blob and foto_blob[0]:
            foto_bytes = foto_blob[0]
            foto_imagen = Image.open(io.BytesIO(foto_bytes))
            foto_imagen = foto_imagen.resize((100, 130), Image.Resampling.LANCZOS)
            foto_tk = ImageTk.PhotoImage(foto_imagen)
            label_foto.config(image=foto_tk)
            label_foto.image = foto_tk
        else:
            # Cargar imagen predeterminada si no hay foto
            cargar_imagen_predeterminada()
    except Exception as e:
        print(f"Error en cargar la foto: {e}")

# Función para cargar la imagen predeterminada
def cargar_imagen_predeterminada():
    try:
        # Asegúrate de que la ruta sea correcta
        imagen_predeterminada = Image.open('logo/logo.jpg')
        imagen_predeterminada = imagen_predeterminada.resize((100, 130), Image.Resampling.LANCZOS)
        foto_tk = ImageTk.PhotoImage(imagen_predeterminada)
        label_foto.config(image=foto_tk)
        label_foto.image = foto_tk
    except Exception as e:
        print(f"Error al cargar la imagen predeterminada: {e}")

# Variable global para almacenar el valor de búsqueda
busqueda_actual = ""

# Función para guardar cambios
def guardar_cambios():
    global foto_ruta, busqueda_actual

    conn = conectar_db()
    cursor = conn.cursor()

    # Obtener las actividades seleccionadas
    actividades_seleccionadas = [checked_listbox.get(i) for i in checked_listbox.curselection()]
    
    # Obtener el ID del registro seleccionado
    id_socis = tree.item(tree.selection())['values'][0]

    # Obtener las actividades actuales del socio
    actividades_actuales = cargar_activitats(id_socis)

    # Actualizar las actividades en la base de datos
    actividades_str = ",".join(actividades_seleccionadas)

    # Si no hay actividades seleccionadas, mantener las actividades actuales
    if not actividades_seleccionadas:
        actividades_str = ",".join(actividades_actuales)

    query = """UPDATE socis SET 
        DNI = %s, 
        Nom = %s, 
        Carrer = %s, 
        Codipostal = %s,
        Poblacio = %s, 
        Provincia = %s, 
        email = %s, 
        Data_naixement = %s,
        Telefon1 = %s, 
        Telefon2 = %s, 
        Telefon3 = %s, 
        Numero_Conta = %s,
        Sepa = %s, 
        Facial = %s, 
        En_ma = %s, 
        Activitats = %s, 
        Quantitat = %s, 
        Alta = %s, 
        Baixa = %s, 
        Data_Inici_activitat = %s, 
        usuari = %s 
    WHERE ID = %s"""

    # Obtener el valor de "Baixa" y manejar el caso de "None"
    baixa_value = entrada_data_baixa.get()  # Obtener el valor directamente
    if baixa_value == "" or baixa_value.lower() == "none":
        baixa_value = None  # Asignar None para que se guarde como NULL en la base de datos
    else:
        # Convertir a formato yyyy-mm-dd
        baixa_value = datetime.strptime(baixa_value, '%d-%m-%Y').strftime('%Y-%m-%d')

    if foto_ruta:
        foto_blob = obtener_foto_blob()
        cursor.execute(query + ", Foto = %s", (
            entrada_dni.get(), entrada_nom.get(), entrada_carrer.get(),
            entrada_codipostal.get(), entrada_poblacio.get(), entrada_provincia.get(),
            entrada_email.get(), entrada_data_naixement.get_date(), entrada_telefon1.get(),
            entrada_telefon2.get(), entrada_telefon3.get(), entrada_numero_conta.get(),
            var_sepa.get(), var_facial.get(), var_en_ma.get(), actividades_str, entrada_quantitat.get(),
            entrada_data_alta.get_date(), baixa_value, entrada_data_inici_activitat.get_date(), entrada_usuari.get(), id_socis, foto_blob
        ))
    else:
        cursor.execute(query, (
            entrada_dni.get(), entrada_nom.get(), entrada_carrer.get(),
            entrada_codipostal.get(), entrada_poblacio.get(), entrada_provincia.get(),
            entrada_email.get(), entrada_data_naixement.get_date(), entrada_telefon1.get(),
            entrada_telefon2.get(), entrada_telefon3.get(), entrada_numero_conta.get(),
            var_sepa.get(), var_facial.get(), var_en_ma.get(), actividades_str, entrada_quantitat.get(),
            entrada_data_alta.get_date(), baixa_value, entrada_data_inici_activitat.get_date(), entrada_usuari.get(), id_socis
        ))

    conn.commit()
    conn.close()

    messagebox.showinfo("Éxit", "Dades actualizades correctament.")
    mostrar_datos(busqueda_actual)

# Función para obtener el BLOB de la foto
def obtener_foto_blob():
    if foto_ruta:
        with open(foto_ruta, 'rb') as file:
            return file.read()
    return None

# Función para cargar una nueva foto
def cargar_nueva_foto():
    global foto_ruta
    selected_item = tree.selection()
    if not selected_item:
        messagebox.showwarning("Selecció", "Si us plau, selecciona un registre per carregar una foto.")
        return

    foto_ruta = filedialog.askopenfilename(filetypes=[("Image Files", "*.jpg;*.jpeg;*.png;*.gif")])
    if foto_ruta:
        try:
            # Leer la foto seleccionada y convertirla a formato compatible
            with open(foto_ruta, 'rb') as file:
                foto_blob = file.read()

            # Obtener el ID del registro seleccionado
            item = tree.item(selected_item)
            id_socio = item['values'][0]

            # Actualizar la foto en la base de datos
            conn = conectar_db()
            cursor = conn.cursor()
            cursor.execute("UPDATE socis SET Foto = %s WHERE ID = %s", (foto_blob, id_socio))
            conn.commit()
            conn.close()

            # Mostrar la foto en la interfaz
            foto_imagen = Image.open(io.BytesIO(foto_blob))
            foto_imagen = foto_imagen.resize((100, 130), Image.Resampling.LANCZOS)
            foto_tk = ImageTk.PhotoImage(foto_imagen)
            label_foto.config(image=foto_tk)
            label_foto.image = foto_tk

            messagebox.showinfo("Èxit", "Foto carregada i guardada correctament.")
        except Exception as e:
            messagebox.showerror("Error", f"No s'ha pogut desar la foto: {e}")
    else:
        messagebox.showinfo("Cancel·lat", "Càrrega de foto cancel·lada.")

# Función para eliminar la foto
def eliminar_foto():
    global foto_ruta
    selected_item = tree.selection()
    if selected_item:
        item = tree.item(selected_item)
        id_socio = item['values'][0]

        respuesta = messagebox.askyesno("Confirma", "Estàs segur que vols eliminar la foto d'aquest registre?")
        if respuesta:
            try:
                conn = conectar_db()
                cursor = conn.cursor()
                cursor.execute("UPDATE socis SET Foto = NULL WHERE ID = %s", (id_socio,))
                conn.commit()
                conn.close()

                # Limpiar la imagen en la interfaz
                foto_ruta = None
                label_foto.config(image='')

                messagebox.showinfo("Èxit", "Foto eliminada correctament.")
            except mysql.connector.Error as e:
                messagebox.showerror("Error ", f"Error en eliminar la foto: {e}")
        else:
            messagebox.showinfo("Cancel·lat", "L'eliminació de la foto ha estat cancel·lada.")
    else:
        messagebox.showwarning("Selecció", "Si us plau, selecciona un registre per eliminar la foto.")

# Configuración de la interfaz gráfica
root = tk.Tk()
root.title("Modificar Socis")

# Establecer el tamaño inicial de la ventana
ancho_inicial = 1240
alto_inicial = 800

# Calcular el nuevo ancho
nuevo_ancho = ancho_inicial + 226  # 6 cm en píxeles

# Configurar el tamaño de la ventana
root.geometry(f"{nuevo_ancho}x{alto_inicial}")

# Crear un Frame para contener el Treeview y el campo de búsqueda
frame_left = tk.Frame(root)
frame_left.pack(side='left', padx=10, pady=20)

# Campo de búsqueda
entrada_busqueda = tk.Entry(frame_left)
entrada_busqueda.pack(pady=20)

# Enlazar el evento de teclear en el campo de búsqueda
entrada_busqueda.bind("<KeyRelease>", buscar)

btn_buscar = tk.Button(frame_left, text="Buscar", command=buscar)
btn_buscar.pack()

# Nuevo botón para recargar la tabla
btn_recargar = tk.Button(frame_left, text="Actualitzar", command=mostrar_datos)
btn_recargar.pack(pady=5)  # Añadir un poco de espacio vertical

# Crear un Frame para contener el Treeview
frame_tree = tk.Frame(frame_left)
frame_tree.pack()

# Configurar el Treeview y mostrar los datos dentro del Frame
tree = ttk.Treeview(frame_tree, columns=("ID", "DNI", "Nom", "Carrer", "Codipostal",
                                         "Poblacio", "Provincia", "Email", "Data_naixement",
                                         "Telefon1", "Telefon2", "Telefon3", "Numero_Conta",
                                         "Sepa", "Activitats", "Quantitat", "Alta", "Baixa",
                                         "Facial", "Data_Inici_activitat", "En_ma", "Data_modificacio"), 
                                         show='headings')

# Configurar columnas del Treeview
for col in tree["columns"]:
    tree.heading(col, text=col, command=lambda c=col: ordenar_tabla(c))

# Ocultar columnas específicas
tree.column("ID", width=0, stretch=False)
tree.column("Numero_Conta", width=0, stretch=False)    
tree.column("Carrer", width=0, stretch=False)    
tree.column("Codipostal", width=0, stretch=False)    
tree.column("Poblacio", width=0, stretch=False)    
tree.column("Provincia", width=0, stretch=False)    
tree.column("Email", width=0, stretch=False)    
tree.column("Data_naixement", width=0, stretch=False)   
tree.column("Telefon1", width=0, stretch=False) 
tree.column("Telefon2", width=0, stretch=False) 
tree.column("Telefon3", width=0, stretch=False) 
tree.column("Sepa", width=0, stretch=False)
tree.column("Quantitat", width=0, stretch=False) 
tree.column("Alta", width=0, stretch=False) 
tree.column("Baixa", width=0, stretch=False) 
tree.column("Facial", width=0, stretch=False) 
tree.column("Data_Inici_activitat", width=0, stretch=False) 
tree.column("En_ma", width=0, stretch=False) 

# Empaquetar el Treeview en el Frame
tree.pack()

# Enlazar el evento para seleccionar elementos en la tabla
tree.bind("<ButtonRelease-1>", cargar_en_formulario)

# Crear un Frame para el formulario
frame_formulario = tk.Frame(root)
frame_formulario.pack(side='right', pady=20, fill='both', expand=True)

# Configurar tamaño mínimo del frame
frame_formulario.config(width=400)

# Campos del formulario
tk.Label(frame_formulario, text="DNI").grid(row=0, column=0)
entrada_dni = tk.Entry(frame_formulario, width=35)
entrada_dni.grid(row=0, column=1)

tk.Label(frame_formulario, text="Nom").grid(row=1, column=0)
entrada_nom = tk.Entry(frame_formulario, width=35)
entrada_nom.grid(row=1, column=1)

tk.Label(frame_formulario, text="Carrer").grid(row=2, column=0)
entrada_carrer = tk.Entry(frame_formulario, width=35)
entrada_carrer.grid(row=2, column=1)

tk.Label(frame_formulario, text="Codipostal").grid(row=3, column=0)
entrada_codipostal = tk.Entry(frame_formulario, width=35)
entrada_codipostal.grid(row=3, column=1)

tk.Label(frame_formulario, text="Població").grid(row=4, column=0)
entrada_poblacio = tk.Entry(frame_formulario, width=35)
entrada_poblacio.grid(row=4, column=1)

tk.Label(frame_formulario, text="Provincia").grid(row=5, column=0)
entrada_provincia = tk.Entry(frame_formulario, width=35)
entrada_provincia.grid(row=5, column=1)

tk.Label(frame_formulario, text="Email").grid(row=6, column=0)
entrada_email = tk.Entry(frame_formulario, width=35)
entrada_email.grid(row=6, column=1)

tk.Label(frame_formulario, text="Data de naixement").grid(row=7, column=0)
entrada_data_naixement = DateEntry(frame_formulario, width=35, date_pattern='dd-mm-yyyy')
entrada_data_naixement.grid(row=7, column=1)

tk.Label(frame_formulario, text="Telefon1").grid(row=8, column=0)
entrada_telefon1 = tk.Entry(frame_formulario, width=35)
entrada_telefon1.grid(row=8, column=1)

tk.Label(frame_formulario, text="Telefon2").grid(row=9, column=0)
entrada_telefon2 = tk.Entry(frame_formulario, width=35)
entrada_telefon2.grid(row=9, column=1)

tk.Label(frame_formulario, text="Telefon3").grid(row=10, column=0)
entrada_telefon3 = tk.Entry(frame_formulario, width=35)
entrada_telefon3.grid(row=10, column=1)

tk.Label(frame_formulario, text="Numero Conta").grid(row=11, column=0)
entrada_numero_conta = tk.Entry(frame_formulario, width=35)
entrada_numero_conta.grid(row=11, column=1)

var_sepa = tk.BooleanVar()
tk.Checkbutton(frame_formulario, text="SEPA", variable=var_sepa).grid(row=13, column=0)

var_facial = tk.BooleanVar()
tk.Checkbutton(frame_formulario, text="Facial", variable=var_facial).grid(row=14, column=0)

var_en_ma = tk.BooleanVar()
tk.Checkbutton(frame_formulario, text="En ma", variable=var_en_ma).grid(row=15, column=0)

tk.Label(frame_formulario, text="Activitats").grid(row=16, column=0)
checked_listbox = tk.Listbox(frame_formulario, selectmode=tk.MULTIPLE)
checked_listbox.grid(row=16, column=1)

# Cargar actividades desde la base de datos
def cargar_activitats_disponibles():
    conn = conectar_db()
    cursor = conn.cursor()
    cursor.execute("SELECT nom FROM activitats")
    actividades = cursor.fetchall()
    conn.close()
    for actividad in actividades:
        checked_listbox.insert(tk.END, actividad[0])

cargar_activitats_disponibles()

tk.Label(frame_formulario, text="Quantitat").grid(row=19, column=0)
entrada_quantitat = tk.Entry(frame_formulario, width=35)
entrada_quantitat.grid(row=19, column=1)

tk.Label(frame_formulario, text="Data d'Alta").grid(row=20, column=0)
entrada_data_alta = DateEntry(frame_formulario, width=35, date_pattern='dd-mm-yyyy')
entrada_data_alta.grid(row=20, column=1)

tk.Label(frame_formulario, text="Data de Baixa").grid(row=21, column=0)
entrada_data_baixa = DateEntry(frame_formulario, width=35, date_pattern='dd-mm-yyyy')
entrada_data_baixa.grid(row=21, column=1)

tk.Label(frame_formulario, text="Data d'Inici Activitat").grid(row=22, column=0)
entrada_data_inici_activitat = DateEntry(frame_formulario, width=35, date_pattern='dd-mm-yyyy')
entrada_data_inici_activitat.grid(row=22, column=1)

# Campo de usuario
tk.Label(frame_formulario, text="Usuari").grid(row=23, column=0)
entrada_usuari = tk.Entry(frame_formulario, width=35)
entrada_usuari.grid(row=23, column=1)

# Label para foto
label_foto = tk.Label(frame_formulario, width=100, height=130)  # Establecer un tamaño fijo
label_foto.place(x=350, y=0)  # Coloca el label en las coordenadas x=350, y=0

btn_cargar_foto = tk.Button(frame_formulario, text="Carregar Foto", command=cargar_nueva_foto)
btn_cargar_foto.grid(row=14, column=2)

btn_eliminar_foto = tk.Button(frame_formulario, text="Eliminar Foto", command=eliminar_foto)
btn_eliminar_foto.grid(row=15, column=2)

btn_eliminar = tk.Button(frame_formulario, text="Eliminar Registre", command=eliminar_registro)
btn_eliminar.grid(row=24, column=0, columnspan=2, pady=10)

# Cambiar el botón "Desa" para que esté en el mismo frame y a la derecha del botón "Eliminar Registre"
btn_guardar = tk.Button(frame_formulario, text="Desa", command=guardar_cambios)
btn_guardar.grid(row=24, column=3, padx=10, pady=10)  # Ajustar la posición

# Variable para controlar el orden de la tabla
orden = 'DESC'

# Inicializar la variable foto_ruta
foto_ruta = None

# Mostrar datos iniciales
mostrar_datos()

root.mainloop()