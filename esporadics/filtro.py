import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import mysql.connector
from PIL import Image, ImageFile, ImageTk
import io
import configparser
from datetime import datetime

def convertir_fecha(fecha_str, formato_entrada='%d-%m-%Y', formato_salida='%Y-%m-%d'):
    if fecha_str and fecha_str != 'None':
        try:
            fecha = datetime.strptime(fecha_str, formato_entrada)
            return fecha.strftime(formato_salida)
        except ValueError:
            return None  # Si no se puede convertir, devuelve None
    return None

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
def cargar_datos(busqueda=None, orden_columna='Baixa', orden='DESC'):
    conn = conectar_db()
    cursor = conn.cursor(dictionary=True)

    query = """SELECT ID, DNI, Nom, Carrer, Codipostal, Poblacio, Provincia, email, 
                Data_naixement, Telefon1, Telefon2, Telefon3, Numero_Conta, Sepa, 
                Activitats, Quantitat, Alta, Baixa, Facial, Data_Inici_activitat, 
                En_ma, usuari FROM esporadics"""
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
def mostrar_datos(busqueda=None, orden_columna='Baixa', orden='DESC'):
    for row in tree.get_children():
        tree.delete(row)

    for row in cargar_datos(busqueda, orden_columna, orden):
        tree.insert('', 'end', values=(
            row['ID'], row['DNI'], row['Nom'], row['Carrer'], row['Codipostal'],
            row['Poblacio'], row['Provincia'], row['email'], row['Data_naixement'],
            row['Telefon1'], row['Telefon2'], row['Telefon3'], row['Numero_Conta'],
            row['Sepa'], row['Activitats'], row['Quantitat'], row['Alta'], row['Baixa'],
            row['Facial'], row['Data_Inici_activitat'], row['En_ma'], row['usuari']
        ))

# Función para ordenar la tabla
def ordenar_tabla(columna):
    global orden
    if columna == 'Baixa':
        orden = 'ASC' if orden == 'DESC' else 'DESC'
    else:
        orden = 'ASC' if orden == 'DESC' else 'DESC'
    mostrar_datos(orden_columna=columna, orden=orden)

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
                cursor.execute("DELETE FROM esporadics WHERE ID = %s", (id_socio,))
                conn.commit()
                conn.close()

                messagebox.showinfo("Éxito", "Registro eliminado correctamente.")
                mostrar_datos()
            except mysql.connector.Error as e:
                messagebox.showerror("Error", f"Error al eliminar el registro: {e}")
        else:
            messagebox.showinfo("Cancelado", "La eliminación ha sido cancelada.")
    else:
        messagebox.showerror("Error", f"Error al eliminar el registro: {e}")

# Función para buscar
def buscar(event=None):
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

        entrada_nom.delete(0, tk.END)
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

        # Convertir fecha de nacimiento
        fecha_naixement = datos[8]
        if fecha_naixement and fecha_naixement != 'None':
            fecha_naixement = datetime.strptime(fecha_naixement, '%Y-%m-%d').strftime('%d-%m-%Y')
        else:
            fecha_naixement = ''
        entrada_data_naixement.delete(0, tk.END)
        entrada_data_naixement.insert(0, fecha_naixement)

        entrada_telefon1.delete(0, tk.END)
        entrada_telefon1.insert(0, datos[9])

        entrada_telefon2.delete(0, tk.END)
        entrada_telefon2.insert(0, datos[10])

        entrada_telefon3.delete(0, tk.END)
        entrada_telefon3.insert(0, datos[11])

        entrada_numero_conta.delete(0, tk.END)
        entrada_numero_conta.insert(0, datos[12])

        var_sepa.set(datos[13] == 1)
        var_facial.set(datos[18] == 1)
        var_en_ma.set(datos[19] == 1)

        cargar_activitats(datos[14])

        entrada_quantitat.delete(0, tk.END)
        entrada_quantitat.insert(0, datos[15])

        # Convertir fecha de alta
        fecha_alta = datos[16]
        if fecha_alta and fecha_alta != 'None':
            fecha_alta = datetime.strptime(fecha_alta, '%Y-%m-%d').strftime('%d-%m-%Y')
        else:
            fecha_alta = ''
        entrada_data_alta.delete(0, tk.END)
        entrada_data_alta.insert(0, fecha_alta)

        # Convertir fecha de baixa
        fecha_baixa = datos[17]
        if fecha_baixa and fecha_baixa != 'None':
            fecha_baixa = datetime.strptime(fecha_baixa, '%Y-%m-%d').strftime('%d-%m-%Y')
        else:
            fecha_baixa = ''
        entrada_data_baixa.delete(0, tk.END)
        entrada_data_baixa.insert(0, fecha_baixa)

        # Convertir fecha de inicio de actividad
        fecha_inici_activitat = datos[19]
        if fecha_inici_activitat and fecha_inici_activitat != 'None':
            fecha_inici_activitat = datetime.strptime(fecha_inici_activitat, '%Y-%m-%d').strftime('%d-%m-%Y')
        else:
            fecha_inici_activitat = ''
        entrada_data_inici_activitat.delete(0, tk.END)
        entrada_data_inici_activitat.insert(0, fecha_inici_activitat)

        entrada_usuari.delete(0, tk.END)
        entrada_usuari.insert(0, datos[21])

        cargar_foto(datos[0])
    

# Función para cargar actividades
def cargar_activitats(activitats):
    for index in range(checked_listbox.size()):
        checked_listbox.selection_clear(index)

    if activitats:
        activitats_seleccionadas = activitats.split(",")
        for i in range(checked_listbox.size()):
            actividad_nombre = checked_listbox.get(i)
            if actividad_nombre.strip() in activitats_seleccionadas:
                checked_listbox.selection_set(i)

# Crear una imagen en blanco para mostrar cuando no hay foto
def crear_imagen_blanco():
    imagen_blanco = Image.new("RGB", (100, 130), (255, 255, 255))  # Color blanco
    return ImageTk.PhotoImage(imagen_blanco)

# Función para cargar la foto
def cargar_foto(id_socio):
    try:
        conn = conectar_db()
        cursor = conn.cursor()
        cursor.execute("SELECT Foto FROM esporadics WHERE ID = %s", (id_socio,))
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
            # Cargar imagen en blanco si no hay foto
            imagen_blanco = crear_imagen_blanco()
            label_foto.config(image=imagen_blanco)
            label_foto.image = imagen_blanco
    except Exception as e:
        print(f"Error al cargar la foto: {e}")

# Variable global para almacenar el valor de búsqueda
busqueda_actual = ""

# Función para guardar cambios
def guardar_cambios():
    global foto_ruta, busqueda_actual
    conn = conectar_db()
    cursor = conn.cursor()

    actividades_seleccionadas = [checked_listbox.get(i) for i in checked_listbox.curselection()]
    actividades_str = ",".join(actividades_seleccionadas)

    # Obtener fechas y convertirlas
    data_naixement = convertir_fecha(entrada_data_naixement.get(), '%d-%m-%Y', '%Y-%m-%d')
    data_alta = convertir_fecha(entrada_data_alta.get(), '%d-%m-%Y', '%Y-%m-%d')
    data_baixa = convertir_fecha(entrada_data_baixa.get(), '%d-%m-%Y', '%Y-%m-%d')
    data_inici_activitat = convertir_fecha(entrada_data_inici_activitat.get(), '%d-%m-%Y', '%Y-%m-%d')

    query = """UPDATE esporadics SET 
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

    id_socis = tree.item(tree.selection())['values'][0]

    if foto_ruta:
        foto_blob = obtener_foto_blob()
        query += ", Foto = %s"
        cursor.execute(query, (
            entrada_dni.get(), entrada_nom.get(), entrada_carrer.get(),
            entrada_codipostal.get(), entrada_poblacio.get(), entrada_provincia.get(),
            entrada_email.get(), data_naixement, entrada_telefon1.get(),
            entrada_telefon2.get(), entrada_telefon3.get(), entrada_numero_conta.get(),
            var_sepa.get(), var_facial.get(), var_en_ma.get(), actividades_str, entrada_quantitat.get(),
            data_alta, data_baixa, data_inici_activitat, entrada_usuari.get(), id_socis, foto_blob
        ))
    else:
        cursor.execute(query, (
            entrada_dni.get(), entrada_nom.get(), entrada_carrer.get(),
            entrada_codipostal.get(), entrada_poblacio.get(), entrada_provincia.get(),
            entrada_email.get(), data_naixement, entrada_telefon1.get(),
            entrada_telefon2.get(), entrada_telefon3.get(), entrada_numero_conta.get(),
            var_sepa.get(), var_facial.get(), var_en_ma.get(), actividades_str, entrada_quantitat.get(),
            data_alta, data_baixa, data_inici_activitat, entrada_usuari.get(), id_socis
        ))

    conn.commit()
    conn.close()

    messagebox.showinfo("Éxito", "Dades actualizades correctament.")
    mostrar_datos(busqueda_actual)

# Función para buscar
def buscar(event=None):
    global busqueda_actual
    busqueda_actual = entrada_busqueda.get()
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
            with open(foto_ruta, 'rb') as file:
                foto_blob = file.read()

            item = tree.item(selected_item)
            id_socio = item['values'][0]

            conn = conectar_db()
            cursor = conn.cursor()
            cursor.execute("UPDATE esporadics SET Foto = %s WHERE ID = %s", (foto_blob, id_socio))
            conn.commit()
            conn.close()

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

        respuesta = messagebox.askyesno("Confirmar", "Estas segur que vols suprimir la fotografia d'aquest registre?")
        if respuesta:
            try:
                conn = conectar_db()
                cursor = conn.cursor()
                cursor.execute("UPDATE esporadics SET Foto = NULL WHERE ID = %s", (id_socio,))
                conn.commit()
                conn.close()

                foto_ruta = None
                label_foto.config(image='')

                messagebox.showinfo("Éxito", "Foto eliminada correctament.")
            except mysql.connector.Error as e:
                messagebox.showerror("Error ", f"Error en eliminar la foto: {e}")
        else:
            messagebox.showinfo("Cancel·lat", "L'eliminació de la foto ha estat cancel·lada.")
    else:
        messagebox.showwarning("Selecció", "Si us plau, selecciona un registre per eliminar la foto.")

# Configuración de la interfaz gráfica
root = tk.Tk()
root.title("Modificar Esporadics")

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
                                         "Facial", "Data_Inici_activitat", "En_ma"), 
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
tree.column("Baixa", width=100, stretch=True)  # Asegúrate de que la columna "Baixa" sea visible
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

tk.Label(frame_formulario, text="Poblacio").grid(row=4, column=0)
entrada_poblacio = tk.Entry(frame_formulario, width=35)
entrada_poblacio.grid(row=4, column=1)

tk.Label(frame_formulario, text="Provincia").grid(row=5, column=0)
entrada_provincia = tk.Entry(frame_formulario, width=35)
entrada_provincia.grid(row=5, column=1)

tk.Label(frame_formulario, text="Email").grid(row=6, column=0)
entrada_email = tk.Entry(frame_formulario, width=35)
entrada_email.grid(row=6, column=1)

tk.Label(frame_formulario, text="Data de naixement").grid(row=7, column=0)
entrada_data_naixement = tk.Entry(frame_formulario, width=35)
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
entrada_numero_conta.grid(row =11, column=1)

var_sepa = tk.BooleanVar()
tk.Checkbutton(frame_formulario, text="SEPA", variable=var_sepa).grid(row=13, column=0)

var_facial = tk.BooleanVar()
tk.Checkbutton(frame_formulario, text="Facial", variable=var_facial).grid(row=14, column=0)

var_en_ma = tk.BooleanVar()
tk.Checkbutton(frame_formulario, text="En ma ", variable=var_en_ma).grid(row=15, column=0)

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
entrada_data_alta = tk.Entry(frame_formulario, width=35)
entrada_data_alta.grid(row=20, column=1)

tk.Label(frame_formulario, text="Data de Baixa").grid(row=21, column=0)
entrada_data_baixa = tk.Entry(frame_formulario, width=35)
entrada_data_baixa.grid(row=21, column=1)

tk.Label(frame_formulario, text="Data d'Inici Activitat").grid(row=22, column=0)
entrada_data_inici_activitat = tk.Entry(frame_formulario, width=35)
entrada_data_inici_activitat.grid(row=22, column=1)

# Campo de usuario
tk.Label(frame_formulario, text="Usuari").grid(row=23, column=0)
entrada_usuari = tk.Entry(frame_formulario, width=35)
entrada_usuari.grid(row=23, column=1)

# Label para foto
label_foto = tk.Label(frame_formulario, width=100, height=130)  # Establecer un tamaño fijo
label_foto.place(x=350, y=0)  # Coloca el label en las coordenadas x=150, y=10

btn_cargar_foto = tk.Button(frame_formulario, text="Carregar Foto", command=cargar_nueva_foto)
btn_cargar_foto.grid(row=14, column=2)

btn_eliminar_foto = tk.Button(frame_formulario, text="Eliminar Foto", command=eliminar_foto)
btn_eliminar_foto.grid(row=15, column=2)

btn_eliminar = tk.Button(frame_formulario, text="Eliminar Registre", command=eliminar_registro)
btn_eliminar.grid(row=24, column=0, columnspan=2, pady=10)

# Cambiar el botón "Desa" para que esté en el mismo frame y a la derecha del botón "Eliminar Registre"
btn_guardar = tk.Button(frame_formulario, text="Desa", command=guardar_cambios)
btn_guardar.grid(row=24, column=2, padx=10, pady=10)  # Ajustar la posición

# Variable para controlar el orden de la tabla
orden = 'DESC'

# Inicializar la variable foto_ruta
foto_ruta = None

# Mostrar datos iniciales
mostrar_datos() 

root.mainloop()