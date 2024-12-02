import subprocess
import tkinter as tk
from tkinter import filedialog, messagebox

def backup_database():
    # Abre un diálogo para seleccionar la ubicación del archivo de respaldo
    file_path = filedialog.asksaveasfilename(defaultextension=".sql",
                                               filetypes=[("SQL files", "*.sql")],
                                               title="Guardar copia de seguridad como")
    if file_path:
        try:
            # Ruta al ejecutable mysqldump
            mysqldump_path = r"\Dinamic\mysql\bin\mysqldump.exe"
            # Comando para hacer la copia de seguridad
            command = [mysqldump_path, "-u", "root", "gimnas"]

            # Abrir el archivo de salida
            with open(file_path, 'w') as output_file:
                subprocess.run(command, stdout=output_file, check=True)

            messagebox.showinfo("Éxito", "Copia de seguridad realizada con éxito.")
        except subprocess.CalledProcessError:
            messagebox.showerror("Error", "Hubo un problema al realizar la copia de seguridad.")
        except Exception as e:
            messagebox.showerror("Error", f"Ocurrió un error: {str(e)}")

# Crear la ventana principal
root = tk.Tk()
root.withdraw()  # Oculta la ventana principal

# Llamar a la función para hacer la copia de seguridad
backup_database()