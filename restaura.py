import subprocess
import tkinter as tk
from tkinter import filedialog, messagebox

def restore_database():
    # Abre un diálogo para seleccionar el archivo de respaldo
    file_path = filedialog.askopenfilename(defaultextension=".sql",
                                            filetypes=[("SQL files", "*.sql")],
                                            title="Seleccionar archivo de copia de seguridad")
    if file_path:
        try:
            # Ruta al ejecutable mysql
            mysql_path = r"C:\xampp\mysql\bin\mysql.exe"
            # Comando para restaurar la base de datos
            command = [mysql_path, "-u", "root", "gimnas"]

            # Ejecutar el comando con el archivo de entrada
            with open(file_path, 'r') as input_file:
                subprocess.run(command, stdin=input_file, check=True)

            messagebox.showinfo("Éxito", "Base de datos restaurada con éxito.")
        except subprocess.CalledProcessError:
            messagebox.showerror("Error", "Hubo un problema al restaurar la base de datos.")
        except Exception as e:
            messagebox.showerror("Error", f"Ocurrió un error: {str(e)}")

# Crear la ventana principal
root = tk.Tk()
root.withdraw()  # Oculta la ventana principal

# Llamar a la función para restaurar la base de datos
restore_database()