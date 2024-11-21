import tkinter as tk
from tkinter import ttk, filedialog
import mysql.connector
from tkinter import messagebox
from PIL import Image, ImageFile, ImageTk
from datetime import datetime
from tkcalendar import Calendar
import io
import configparser  # Import configparser to read the config.ini file

# Permitir la carga de imágenes truncadas
ImageFile.LOAD_TRUNCATED_IMAGES = True

# Read database configuration from config.ini
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
def cargar_datos(busqueda=None):
    conn = conectar_db()
    cursor = conn.cursor(dictionary=True)

    query = "SELECT ID, DNI, Nom, Carrer, Codipostal, Poblacio, Provincia, email, Data_naixement, Telefon1, Telefon2, Telefon3, Numero_Conta, Sepa, Activitats, Quantitat, Alta, Baixa, Facial, Data_Inici_activitat, En_ma FROM esporadics"
    if busqueda:
        query += " WHERE Nom LIKE %s OR DNI LIKE %s"
        cursor.execute(query, ('%' + busqueda + '%', '%' + busqueda + '%'))
    else:
        cursor.execute(query)

    rows = cursor.fetchall()
    conn.close()
    return rows

# Función para eliminar el registro seleccionado
def eliminar_registro():
    # Obtener el ID del socio seleccionado en el Treeview
    selected_item = tree.selection()
    if selected_item:
        item = tree.item(selected_item)
        id_socio = item['values'][0]  # Obtener el ID del socio

        # Confirmar la eliminación
        respuesta = messagebox.askyesno("Confirmar", "¿Estás seguro de que quieres eliminar este registro?")
        if respuesta:
            try:
                # Conectar a la base de datos y eliminar el registro
                conn = conectar_db()
                cursor = conn.cursor()
                cursor.execute("DELETE FROM esporadics WHERE ID = %s", (id_socio,))
                conn.commit()
                conn.close()

                # Mostrar un mensaje de éxito
                messagebox.showinfo("Éxito", "Registro eliminado correctamente.")
                mostrar_datos()  # Volver a mostrar los datos en el Treeview después de la eliminación
            except mysql.connector.Error as e:
                messagebox.showerror("Error", f"Error al eliminar el registro: {e}")
        else:
            messagebox.showinfo("Cancelado", "La eliminación ha sido cancelada.")
    else:
        messagebox.showwarning("Selección", "Por favor, selecciona un registro para eliminar.")

# Función para mostrar los datos en el Treeview
def mostrar_datos(busqueda=None):
    # Limpiar los datos anteriores del Treeview
    for row in tree.get_children():
        tree.delete(row)

    # Insertar los nuevos datos del socio
    for row in cargar_datos(busqueda):
        tree.insert('', 'end', values=(
            row['ID'], row['DNI'], row['Nom'], row['Carrer'], row['Codipostal'],
            row['Poblacio'], row['Provincia'], row['email'], row['Data_naixement'],
            row['Telefon1'], row['Telefon2'], row['Telefon3'], row['Numero_Conta'],
            row['Sepa'], row['Activitats'], row['Quantitat'], row['Alta'], row['Baixa'],
            row['Facial'], row['Data_Inici_activitat'], row['En_ma']  # Asegúrate de que esta columna esté aquí
        ))


# Función para buscar
def buscar():
    busqueda = entrada_busqueda.get()
    mostrar_datos(busqueda)

# Función para cargar datos en el formulario
def cargar_en_formulario(event):
    selected_item = tree.selection()  # Obtenemos el elemento seleccionado
    if selected_item:  # Solo si hay un elemento seleccionado
        item = tree.item(selected_item)  # Obtenemos los detalles del item
        datos = item['values']
        
        # Llenamos los campos del formulario con los datos del socio seleccionado
        entrada_dni.delete(0, tk.END)
        entrada_dni.insert(0, datos[1])  # DNI

        entrada_nom.delete(0, tk.END)
        entrada_nom.insert(0, datos[2])  # Nombre

        entrada_carrer.delete(0, tk.END)
        entrada_carrer.insert(0, datos[3])  # Calle

        entrada_codipostal.delete(0, tk.END)
        entrada_codipostal.insert(0, datos[4])  # Código postal

        entrada_poblacio.delete(0, tk.END)
        entrada_poblacio.insert(0, datos[5])  # Población

        entrada_provincia.delete(0, tk.END)
        entrada_provincia.insert(0, datos[6])  # Provincia

        entrada_email.delete(0, tk.END)
        entrada_email.insert(0, datos[7])  # Email

        entrada_data_naixement.delete(0, tk.END)
        entrada_data_naixement.insert(0, datos[8])  # Fecha de nacimiento

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

        # Cargar actividades en el checked listbox
        cargar_activitats(datos[14])  # Activitats del socio seleccionado

        entrada_quantitat.delete(0, tk.END)
        entrada_quantitat.insert(0, datos[15])  # Quantitat
        
        # Cargar las nuevas fechas
        entrada_data_alta.delete(0, tk.END)
        entrada_data_alta.insert(0, datos[16])  # Data d'Alta

        entrada_data_baixa.delete(0, tk.END)
        entrada_data_baixa.insert(0, datos[17])  # Data de Baixa

        entrada_data_inici_activitat.delete(0, tk.END)
        entrada_data_inici_activitat.insert(0, datos[19])  # Data d'Inici Activitat
               
        # Cargar foto
        cargar_foto(datos[0])  # ID del socio seleccionado


# Función para cargar actividades
def cargar_activitats(activitats):
    for index in range(checked_listbox.size()):
        checked_listbox.selection_clear(index)

    if activitats:
        activitats_seleccionadas = activitats.split(",")  # Suponiendo que las actividades están separadas por comas
        for i in range(checked_listbox.size()):
            actividad_nombre = checked_listbox.get(i)
            if actividad_nombre.strip() in activitats_seleccionadas:  # .strip() para eliminar espacios
                checked_listbox.selection_set(i)

# Función para cargar la foto
def cargar_foto(id_socio):
    try:
        conn = conectar_db()
        cursor = conn.cursor()
        cursor.execute("SELECT Foto FROM esporadics WHERE ID = %s", (id_socio,))
        foto_blob = cursor.fetchone()
        conn.close()

        if foto_blob and foto_blob[0]:  # Verifica que se encontró una foto
            foto_bytes = foto_blob[0]
            # Crear un objeto de imagen a partir de los bytes
            foto_imagen = Image.open(io.BytesIO(foto_bytes))
            # Redimensionar la imagen a 100x130 píxeles
            foto_imagen = foto_imagen.resize((100, 130), Image.Resampling.LANCZOS)
            # Convertir a PhotoImage
            foto_tk = ImageTk.PhotoImage(foto_imagen)
            # Mostrar la foto en el label
            label_foto.config(image=foto_tk)
            label_foto.image = foto_tk  # Mantener referencia
        else:
            label_foto.config(image='')  # Limpiar el label si no hay foto
    except Exception as e:
        print(f"Error al cargar la foto: {e}")  # Mostrar el error en la consola

# Función para guardar cambios
def guardar_cambios():
    conn = conectar_db()
    cursor = conn.cursor()

    actividades_seleccionadas = [checked_listbox.get(i) for i in checked_listbox.curselection()]
    actividades_str = ",".join(actividades_seleccionadas)

    query = """UPDATE esporadics SET DNI = %s, Nom = %s, Carrer = %s, Codipostal = %s,
               Poblacio = %s, Provincia = %s, email = %s, Data_naixement = %s,
               Telefon1 = %s, Telefon2 = %s, Telefon3 = %s, Numero_Conta = %s,
               Sepa = %s, Facial = %s, En_ma = %s, Activitats = %s, Foto = %s WHERE ID = %s"""

    id_socis = tree.item(tree.selection())['values'][0]  # Obtener el ID del socio seleccionado
    foto_blob = obtener_foto_blob()  # Obtener la foto en formato BLOB

    cursor.execute(query, (
        entrada_dni.get(), entrada_nom.get(), entrada_carrer.get(),
        entrada_codipostal.get(), entrada_poblacio.get(), entrada_provincia.get(),
        entrada_email.get(), entrada_data_naixement.get(), entrada_telefon1.get(),
        entrada_telefon2.get(), entrada_telefon3.get(), entrada_numero_conta.get(),
        var_sepa.get(), var_facial.get(), var_en_ma.get(), actividades_str, foto_blob, id_socis
    ))
    conn.commit()
    conn.close()

    messagebox.showinfo("Éxito", "Dades actualizades correctament.")
    mostrar_datos()  # Volver a mostrar los datos actualizados en la tabla

# Función para obtener el BLOB de la foto
def obtener_foto_blob():
    if foto_ruta:
        with open(foto_ruta, 'rb') as file:
            return file.read()
    return None


# Función para cargar una nueva foto
def cargar_nueva_foto():
    global foto_ruta
    foto_ruta = filedialog.askopenfilename(filetypes=[("Image Files", "*.jpg;*.jpeg;*.png;*.gif")])
    if foto_ruta:
        # Mostrar la nueva foto en el Label
        foto_imagen = Image.open(foto_ruta)
        foto_imagen = foto_imagen.resize((100, 130), Image.Resampling.LANCZOS)  # Cambiar el tamaño a 100x130
        foto_tk = ImageTk.PhotoImage(foto_imagen)

        # Mostrar la imagen en el Label
        label_foto.config(image=foto_tk)
        label_foto.image = foto_tk  # Mantener una referencia para evitar que se elimine el objeto
    else:
        label_foto.config(image='')  # Si no se selecciona foto, borrar la imagen

# Función para eliminar la foto
def eliminar_foto():
    global foto_ruta
    foto_ruta = None
    label_foto.config(image='')  # Borrar la imagen

# Configuración de la interfaz gráfica
root = tk.Tk()
root.title("Modificar Socis")

# Frame para el formulario
frame_formulario = tk.Frame(root)
frame_formulario.pack(pady=40)

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

# Etiqueta para la fecha de nacimiento
tk.Label(frame_formulario, text="Data de naixement").grid(row=7, column=0)

# Crear la función que muestra el calendario cuando el campo de entrada recibe el foco
def mostrar_calendario(event):
    # Crear un calendario emergente
    calendario = Calendar(frame_formulario, selectmode='day', date_pattern='dd/mm/yyyy')
    calendario.grid(row=8, column=1)
    
    # Función que se ejecuta cuando se selecciona una fecha en el calendario
    def obtener_fecha(event):
        entrada_data_naixement.delete(0, tk.END)
        entrada_data_naixement.insert(0, calendario.get_date())
        calendario.grid_forget()  # Ocultar el calendario después de seleccionar la fecha

    # Vinculamos la selección de fecha al calendario
    calendario.bind("<<CalendarSelected>>", obtener_fecha)

# Entrada de texto para la fecha de nacimiento
entrada_data_naixement = tk.Entry(frame_formulario, width=35)
entrada_data_naixement.grid(row=7, column=1)

# Configurar el evento de clic en el campo de entrada para mostrar el calendario
entrada_data_naixement.bind("<FocusIn>", mostrar_calendario)
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
tk.Checkbutton(frame_formulario, text="SEPA", variable=var_sepa).grid(row=12, column=0)

var_facial = tk.BooleanVar()
tk.Checkbutton(frame_formulario, text="Facial", variable=var_facial).grid(row=13, column=0)

var_en_ma = tk.BooleanVar()
tk.Checkbutton(frame_formulario, text="En ma", variable=var_en_ma).grid(row=14, column=0)

# Campo de actividades
tk.Label(frame_formulario, text="Activitats").grid(row=15, column=0)
checked_listbox = tk.Listbox(frame_formulario, selectmode=tk.MULTIPLE)
checked_listbox.grid(row=15, column=1)

# Cargar actividades desde la base de datos
def cargar_activitats_disponibles():
    conn = conectar_db()
    cursor = conn.cursor()
    cursor.execute("SELECT nom FROM activitats")  # Suponiendo que la tabla de actividades se llama 'activitats'
    actividades = cursor.fetchall()
    conn.close()
    for actividad in actividades:
        checked_listbox.insert(tk.END, actividad[0])

cargar_activitats_disponibles()

# Añadir el campo Quantitat debajo de Activitats
tk.Label(frame_formulario, text="Quantitat").grid(row=18, column=0)
entrada_quantitat = tk.Entry(frame_formulario, width=35)
entrada_quantitat.grid(row=18, column=1)

# Añadir las etiquetas y los campos de entrada para las nuevas fechas
tk.Label(frame_formulario, text="Data d'Alta").grid(row=19, column=0)
entrada_data_alta = tk.Entry(frame_formulario, width=35)
entrada_data_alta.grid(row=19, column=1)

tk.Label(frame_formulario, text="Data de Baixa").grid(row=20, column=0)
entrada_data_baixa = tk.Entry(frame_formulario, width=35)
entrada_data_baixa.grid(row=20, column=1)

tk.Label(frame_formulario, text="Data d'Inici Activitat").grid(row=21, column=0)
entrada_data_inici_activitat = tk.Entry(frame_formulario, width=35)
entrada_data_inici_activitat.grid(row=21, column=1)

# Añadir las funciones para mostrar el calendario cuando el campo de entrada recibe el foco
def mostrar_calendario_alta(event):
    calendario = Calendar(frame_formulario, selectmode='day', date_pattern='dd/mm/yyyy')
    calendario.grid(row=18, column=1)

    def obtener_fecha_alta(event):
        entrada_data_alta.delete(0, tk.END)
        entrada_data_alta.insert(0, calendario.get_date())
        calendario.grid_forget()

    calendario.bind("<<CalendarSelected>>", obtener_fecha_alta)

def mostrar_calendario_baixa(event):
    calendario = Calendar(frame_formulario, selectmode='day', date_pattern='dd/mm/yyyy')
    calendario.grid(row=18, column=1)

    def obtener_fecha_baixa(event):
        entrada_data_baixa.delete(0, tk.END)
        entrada_data_baixa.insert(0, calendario.get_date())
        calendario.grid_forget()

    calendario.bind("<<CalendarSelected>>", obtener_fecha_baixa)

def mostrar_calendario_inici_activitat(event):
    calendario = Calendar(frame_formulario, selectmode='day', date_pattern='dd/mm/yyyy')
    calendario.grid(row=18, column=1)

    def obtener_fecha_inici_activitat(event):
        entrada_data_inici_activitat.delete(0, tk.END)
        entrada_data_inici_activitat.insert(0, calendario.get_date())
        calendario.grid_forget()

    calendario.bind("<<CalendarSelected>>", obtener_fecha_inici_activitat)
    
    # Configurar los eventos de clic en los campos de entrada para mostrar el calendario
entrada_data_alta.bind("<FocusIn>", mostrar_calendario_alta)
entrada_data_baixa.bind("<FocusIn>", mostrar_calendario_baixa)
entrada_data_inici_activitat.bind("<FocusIn>", mostrar_calendario_inici_activitat)

# Label para mostrar la foto
label_foto = tk.Label(root)  # Cambia a root para que esté fuera del frame
# Calcular la distancia en píxeles para 3 cm
distancia_cm_a_pixeles = 3 * 37.8  # 3 cm en píxeles

# Definir la posición de la imagen en relación con el campo de texto del DNI
# Suponiendo que el campo de entrada 'entrada_dni' está en la fila 0, columna 1
# Puedes usar la propiedad `winfo_height()` de la entrada para obtener su altura y ajustarla en consecuencia
altura_dni = entrada_dni.winfo_height()

# Establecer la posición de la foto a 3 cm debajo del campo DNI
label_foto.place(x=entrada_dni.winfo_x() + entrada_dni.winfo_width() + 10, y=entrada_dni.winfo_y() + altura_dni + distancia_cm_a_pixeles)

# Botón para cargar nueva foto
btn_cargar_foto = tk.Button(frame_formulario, text="Carregar Foto", command=cargar_nueva_foto)
btn_cargar_foto.grid(row=14, column=2)

# Botón para eliminar la foto
btn_eliminar_foto = tk.Button(frame_formulario, text="Eliminar Foto", command=eliminar_foto)
btn_eliminar_foto.grid(row=15, column=2)

# Botón para eliminar registro
btn_eliminar = tk.Button(root, text="Eliminar Registro", command=eliminar_registro)
btn_eliminar.pack(pady=10)

# Botón para guardar cambios
btn_guardar = tk.Button(root, text="Desa", command=guardar_cambios)
btn_guardar.pack(pady=20)

# Configurar el Treeview y mostrar los datos
tree = ttk.Treeview(root, columns=("ID", "DNI", "Nom", "Carrer", "Codipostal",
                                    "Poblacio", "Provincia", "Email", "Data_naixement",
                                    "Telefon1", "Telefon2", "Telefon3", "Numero_Conta",
                                    "Sepa", "Activitats", "Quantitat", "Alta", "Baixa",
                                    "Facial", "Data_Inici_activitat", "En_ma"), show='headings')
tree.pack(pady=20)

# Configurar columnas
for col in tree["columns"]:
    tree.heading(col, text=col, command=lambda _col=col: ordenar_por_columna(_col))
    
# Ocultar columnas específicas (por ejemplo, "ID" y "Numero_Conta")
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

tree.bind("<ButtonRelease-1>", cargar_en_formulario)

# # Diccionario para almacenar el estado de ordenación de las columnas
ordenacion_estado = {}

def ordenar_por_columna(col):
    # Cambiar el estado de ordenación de la columna
    if col not in ordenacion_estado:
        ordenacion_estado[col] = True  # Orden ascendente por defecto
    else:
        ordenacion_estado[col] = not ordenacion_estado[col]  # Invertir el estado

    # Obtener los datos de la columna
    lista_datos = [(tree.set(k, col), k) for k in tree.get_children('')]

    # Cambiar el texto de la cabecera para mostrar el estado de ordenación
    for item in tree["columns"]:
        tree.heading(item, text=item)  # Reiniciar texto de cabeceras

    tree.heading(col, text=col + (" ↓" if ordenacion_estado[col] else " ↑"))  # Actualizar la cabecera con el estado

    # Rearmar los elementos en el Treeview
    for index, (val, k) in enumerate(lista_datos):
        tree.move(k, '', index)
        
# Mostrar datos iniciales
mostrar_datos()

# Campo de búsqueda
entrada_busqueda = tk.Entry(root)
entrada_busqueda.pack(pady=20)

btn_buscar = tk.Button(root, text="Buscar", command=buscar)
btn_buscar.pack()

# Mostrar datos iniciales
mostrar_datos()

root.mainloop()
