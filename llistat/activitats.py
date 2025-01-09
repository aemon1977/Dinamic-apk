import tkinter as tk
from tkinter import ttk, messagebox
import mysql.connector
import configparser

# Cargar configuración desde config.ini
config = configparser.ConfigParser()
config.read("config.ini")

# Configuración de la base de datos
db_config = {
    'host': config.get("mysql", "host"),
    'user': config.get("mysql", "user"),
    'password': config.get("mysql", "password"),
    'database': config.get("mysql", "database")
}

# Función para conectar con la base de datos
def connect_db():
    return mysql.connector.connect(**db_config)

# Función para agregar una nueva actividad
def agregar_actividad():
    nombre = entry_nom.get().strip()
    if nombre:
        try:
            conn = connect_db()
            cursor = conn.cursor()
            cursor.execute("INSERT INTO activitats (nom) VALUES (%s)", (nombre,))
            conn.commit()
            conn.close()
            messagebox.showinfo("Èxit", "Activitat afegida amb èxit.")
            entry_nom.delete(0, tk.END)
            cargar_activitats()
        except mysql.connector.Error as err:
            messagebox.showerror("Error", f"Error a l'afegir l'activitat: {err}")
    else:
        messagebox.showwarning("Avís", "El camp de nom és obligatori.")

# Función para eliminar una actividad de la tabla 'activitats' y de la columna 'activitats' de la tabla 'socis'
def eliminar_actividad():
    seleccion = tree.selection()
    if not seleccion:
        messagebox.showwarning("Avís", "Selecciona una activitat per eliminar.")
        return

    id_activitat = tree.item(seleccion)['values'][0]

    if messagebox.askyesno("Confirmació", "Estàs segur que vols eliminar aquesta activitat?"):
        try:
            conn = connect_db()
            cursor = conn.cursor()

            # Obtener el nombre de la actividad por su ID
            cursor.execute("SELECT nom FROM activitats WHERE id = %s", (id_activitat,))
            actividad_nombre = cursor.fetchone()
            if actividad_nombre:
                actividad_nombre = actividad_nombre[0]

                # Eliminar la actividad de los socios
                cursor.execute("""
                    UPDATE socis
                    SET activitats = REPLACE(activitats, %s, '')
                    WHERE FIND_IN_SET(%s, activitats) > 0
                """, (actividad_nombre, actividad_nombre))

                cursor.execute("""
                    UPDATE socis
                    SET activitats = TRIM(BOTH ',' FROM activitats)
                    WHERE FIND_IN_SET(%s, activitats) > 0
                """, (actividad_nombre,))

                conn.commit()

                # Eliminar la actividad de la tabla 'activitats'
                cursor.execute("DELETE FROM activitats WHERE id = %s", (id_activitat,))
                conn.commit()

                conn.close()
                cargar_activitats()
                messagebox.showinfo("Èxit", "Activitat eliminada amb èxit.")
            else:
                messagebox.showerror("Error", "Activitat no trobada.")
        except mysql.connector.Error as err:
            messagebox.showerror("Error", f"Error al eliminar la activitat: {err}")

# Función para cargar actividades en la tabla
def cargar_activitats():
    for item in tree.get_children():
        tree.delete(item)
    try:
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM activitats")
        rows = cursor.fetchall()
        conn.close()
        for row in rows:
            tree.insert("", "end", values=row)
        ajustar_columnas()
    except mysql.connector.Error as err:
        messagebox.showerror("Error", f"Error a carregar les activitats: {err}")

# Función para ajustar el tamaño de las columnas al contenido
def ajustar_columnas():
    for col in tree["columns"]:
        max_length = max(
            [len(str(tree.set(item, col))) for item in tree.get_children()] + [len(col)]
        )
        tree.column(col, width=max_length * 10, stretch=True)

# Configuración de la ventana principal
root = tk.Tk()
root.title("Gestionar Activitats")

# Sección para agregar actividades
frame_agregar = tk.Frame(root)
frame_agregar.pack(pady=10)

label_nom = tk.Label(frame_agregar, text="Nom de l'activitat:")
label_nom.grid(row=0, column=0, padx=5, pady=5)

entry_nom = tk.Entry(frame_agregar)
entry_nom.grid(row=0, column=1, padx=5, pady=5)

btn_desa = tk.Button(frame_agregar, text="Desa", command=agregar_actividad)
btn_desa.grid(row=0, column=2, padx=5, pady=5)

# Sección para mostrar la lista de actividades
label_llista = tk.Label(root, text="Llista d'Activitats")
label_llista.pack()

tree = ttk.Treeview(root, columns=("ID", "Nom"), show="headings")
tree.heading("ID", text="ID")
tree.heading("Nom", text="Nom")
tree.pack(padx=10, pady=5)

# Botón para eliminar una actividad seleccionada
btn_eliminar = tk.Button(root, text="Eliminar Seleccionat", command=eliminar_actividad)
btn_eliminar.pack(pady=5)

# Cargar las actividades al iniciar la aplicación
cargar_activitats()

# Ejecutar la aplicación
root.mainloop()
