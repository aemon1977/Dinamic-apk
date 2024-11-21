import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk
import mysql.connector
from datetime import datetime
from tkcalendar import Calendar
import io

class GymManagementSystem:
    def __init__(self, root):
        self.root = root
        self.root.title("Gestió de esporadics del Gimnàs")
        self.root.geometry("800x1000")

        # Configuración de la base de datos
        self.db_config = {
            'host': 'localhost',
            'user': 'root',
            'password': '',
            'database': 'gimnas'
        }

        # Crear el marco principal
        self.main_frame = ttk.Frame(root, padding="20")
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # Variables de formulario
        self.dni_var = tk.StringVar()
        self.nom_var = tk.StringVar()
        self.carrer_var = tk.StringVar()
        self.cp_var = tk.StringVar()
        self.poblacio_var = tk.StringVar()
        self.provincia_var = tk.StringVar()
        self.email_var = tk.StringVar()
        self.data_naixement_var = tk.StringVar()
        self.telefon1_var = tk.StringVar()
        self.telefon2_var = tk.StringVar()
        self.telefon3_var = tk.StringVar()
        self.compte_var = tk.StringVar()
        self.sepa_var = tk.BooleanVar()
        self.quantitat_var = tk.StringVar()
        self.alta_var = tk.StringVar()
        self.baixa_var = tk.StringVar()
        self.facial_var = tk.BooleanVar()
        self.data_inici_var = tk.StringVar()
        self.usuari_var = tk.StringVar()
        self.photo_data = None

        self.create_widgets()
        self.load_activities()

    # Método para limpiar el formulario
    def clear_form(self):
        self.dni_var.set("")
        self.nom_var.set("")
        self.carrer_var.set("")
        self.cp_var.set("")
        self.poblacio_var.set("")
        self.provincia_var.set("")
        self.email_var.set("")
        self.data_naixement_var.set("")
        self.telefon1_var.set("")
        self.telefon2_var.set("")
        self.telefon3_var.set("")
        self.compte_var.set("")
        self.sepa_var.set(False)
        self.quantitat_var.set("")
        self.alta_var.set("")
        self.baixa_var.set("")
        self.facial_var.set(False)
        self.data_inici_var.set("")
        self.usuari_var.set("")
        self.activities_listbox.selection_clear(0, tk.END)
        self.photo_label.config(image="")  # Restablece la imagen de la foto
        self.photo_data = None

    def lookup_postal_code(self, event=None):
        postal_code = self.cp_var.get().strip()
        if postal_code:
            try:
                conn = mysql.connector.connect(**self.db_config)
                cursor = conn.cursor(dictionary=True)
                query = "SELECT poblacio, provincia FROM codipostal WHERE cp = %s"
                cursor.execute(query, (postal_code,))
                result = cursor.fetchone()

                if result:
                    self.poblacio_var.set(result['poblacio'])
                    self.provincia_var.set(result['provincia'])
                else:
                    self.poblacio_var.set('')
                    self.provincia_var.set('')
                    messagebox.showwarning("No trobat", "Codi postal no trobat a la base de dades.")

                cursor.close()
                conn.close()

            except mysql.connector.Error as err:
                messagebox.showerror("Error de base de dades", f"Error al consultar la base de dades: {err}")

    def create_widgets(self):
        title_label = ttk.Label(self.main_frame, text="Afegir esporadics", font=('Helvetica', 24, 'bold'))
        title_label.grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 20))

        fields = [
            ("DNI:", self.dni_var),
            ("Nom:", self.nom_var),
            ("Carrer:", self.carrer_var),
            ("Codi Postal:", self.cp_var),
            ("Població:", self.poblacio_var),
            ("Província:", self.provincia_var),
            ("Email:", self.email_var),
            ("Data de naixement:", self.data_naixement_var),
            ("Telèfon 1:", self.telefon1_var),
            ("Telèfon 2:", self.telefon2_var),
            ("Telèfon 3:", self.telefon3_var),
            ("Número de Compte:", self.compte_var),
        ]

        left_frame = ttk.Frame(self.main_frame)
        left_frame.grid(row=1, column=0, sticky="nsew", padx=(0, 20))

        for i, (label_text, var) in enumerate(fields):
            ttk.Label(left_frame, text=label_text).grid(row=i, column=0, sticky="w", pady=5)
            if label_text == "Codi Postal:":
                entry = ttk.Entry(left_frame, textvariable=var, width=40)
                entry.grid(row=i, column=1, sticky="w", pady=5)
                entry.bind('<FocusOut>', self.lookup_postal_code)
                entry.bind('<Return>', self.lookup_postal_code)
            elif label_text == "Data de naixement:":
                entry = ttk.Entry(left_frame, textvariable=var, width=40)
                entry.grid(row=i, column=1, sticky="w", pady=5)
                entry.bind('<1>', lambda event, var=var: self.show_calendar(event, var))
            elif label_text in ["Població:", "Província:"]:
                entry = ttk.Entry(left_frame, textvariable=var, width=40, state='readonly')
                entry.grid(row=i, column=1, sticky="w", pady=5)
            else:
                ttk.Entry(left_frame, textvariable=var, width=40).grid(row=i, column=1, sticky="w", pady=5)

        ttk.Checkbutton(left_frame, text="SEPA", variable=self.sepa_var).grid(row=len(fields), column=1, sticky="w", pady=5)

        ttk.Label(left_frame, text="Activitats:").grid(row=len(fields) + 1, column=0, sticky="nw", pady=5)
        self.activities_listbox = tk.Listbox(left_frame, selectmode="multiple", height=5, exportselection=0)
        self.activities_listbox.grid(row=len(fields) + 1, column=1, sticky="w", pady=5)

        ttk.Label(left_frame, text="Quantitat:").grid(row=len(fields) + 2, column=0, sticky="w", pady=5)
        ttk.Entry(left_frame, textvariable=self.quantitat_var, width=40).grid(row=len(fields) + 2, column=1, sticky="w", pady=5)

        ttk.Label(left_frame, text="Data d'alta:").grid(row=len(fields) + 3, column=0, sticky="w", pady=5)
        alta_entry = ttk.Entry(left_frame, textvariable=self.alta_var, width=40)
        alta_entry.grid(row=len(fields) + 3, column=1, sticky="w", pady=5)
        alta_entry.bind('<1>', lambda event, var=self.alta_var: self.show_calendar(event, var))

        ttk.Label(left_frame, text="Data de baixa:").grid(row=len(fields) + 4, column=0, sticky="w", pady=5)
        baixa_entry = ttk.Entry(left_frame, textvariable=self.baixa_var, width=40)
        baixa_entry.grid(row=len(fields) + 4, column=1, sticky="w", pady=5)
        baixa_entry.bind('<1>', lambda event, var=self.baixa_var: self.show_calendar(event, var))

        ttk.Checkbutton(left_frame, text="Facial", variable=self.facial_var).grid(row=len(fields) + 5, column=1, sticky="w", pady=5)

        ttk.Label(left_frame, text="Data d'inici activitat:").grid(row=len(fields) + 6, column=0, sticky="w", pady=5)
        data_inici_entry = ttk.Entry(left_frame, textvariable=self.data_inici_var, width=40)
        data_inici_entry.grid(row=len(fields) + 6, column=1, sticky="w", pady=5)
        data_inici_entry.bind('<1>', lambda event, var=self.data_inici_var: self.show_calendar(event, var))

        ttk.Label(left_frame, text="Usuari:").grid(row=len(fields) + 7, column=0, sticky="w", pady=5)
        ttk.Entry(left_frame, textvariable=self.usuari_var, width=40).grid(row=len(fields) + 7, column=1, sticky="w", pady=5)

        photo_frame = ttk.Frame(self.main_frame)
        photo_frame.grid(row=1, column=1, sticky="nsew", padx=(20, 0))
        self.photo_label = ttk.Label(photo_frame, text="Foto")
        self.photo_label.pack(pady=5)
        upload_btn = ttk.Button(photo_frame, text="Carregar foto", command=self.upload_photo)
        upload_btn.pack(pady=5)

        ttk.Button(left_frame, text="Afegir", command=self.submit_form, width=20).grid(
            row=len(fields) + 8, column=1, pady=20, sticky="e"
        )

    def show_calendar(self, event, date_var):
        top = tk.Toplevel(self.root)
        top.title("Selecciona una data")
        cal = Calendar(top, selectmode='day', date_pattern='dd-mm-yyyy')

        def set_date():
            date_var.set(cal.get_date())
            top.destroy()

        cal.pack(pady=20)
        ttk.Button(top, text="Seleccionar", command=set_date).pack()

    def load_activities(self):
        try:
            conn = mysql.connector.connect(**self.db_config)
            cursor = conn.cursor()
            cursor.execute("SELECT nom FROM activitats")
            activities = cursor.fetchall()

            for activity in activities:
                self.activities_listbox.insert(tk.END, activity[0])

            cursor.close()
            conn.close()

        except mysql.connector.Error as err:
            messagebox.showerror("Error de base de dades", f"Error al carregar les activitats: {err}")

    def upload_photo(self):
        file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.jpg;*.jpeg;*.png")])
        if file_path:
            image = Image.open(file_path)
            if image.mode == 'RGBA':
                image = image.convert('RGB')
            image = image.resize((150, 200))
            buffered = io.BytesIO()
            image.save(buffered, format="JPEG")
            self.photo_data = buffered.getvalue()

            image_tk = ImageTk.PhotoImage(image)
            self.photo_label.config(image=image_tk)
            self.photo_label.image = image_tk

    def submit_form(self):
        dni = self.dni_var.get().strip()
        nom = self.nom_var.get().strip()
        carrer = self.carrer_var.get().strip()
        cp = self.cp_var.get().strip()
        poblacio = self.poblacio_var.get().strip()
        provincia = self.provincia_var.get().strip()
        email = self.email_var.get().strip()
        
        data_naixement = self.convert_date(self.data_naixement_var.get())
        alta = self.convert_date(self.alta_var.get())
        baixa = self.convert_date(self.baixa_var.get())
        data_inici = self.convert_date(self.data_inici_var.get())
        
        telefon1 = self.telefon1_var.get().strip()
        telefon2 = self.telefon2_var.get().strip()
        telefon3 = self.telefon3_var.get().strip()
        compte = self.compte_var.get().strip()
        sepa = self.sepa_var.get()
        quantitat = self.quantitat_var.get().strip()
        facial = self.facial_var.get()
        usuari = self.usuari_var.get().strip()
        
        data_modificacio = datetime.now().strftime("%Y-%m-%d")

        try:
            conn = mysql.connector.connect(**self.db_config)
            cursor = conn.cursor()

            if not dni:
                cursor.execute("SELECT id FROM esporadics ORDER BY id DESC LIMIT 1")
                last_id = cursor.fetchone()
                next_id = (last_id[0] + 1) if last_id else 1
                dni = f"SOCI{next_id:05d}"

            selected_activities = [self.activities_listbox.get(i) for i in self.activities_listbox.curselection()]
            activities_str = ",".join(selected_activities)

            query = """
                INSERT INTO esporadics (dni, nom, carrer, codipostal, poblacio, provincia, email, data_naixement, telefon1, telefon2, telefon3,
                numero_conta, sepa, quantitat, alta, baixa, facial, Data_Inici_activitat, usuari, foto, activitats)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            values = (dni, nom, carrer, cp, poblacio, provincia, email, data_naixement, telefon1, telefon2, telefon3,
                      compte, sepa, quantitat, alta, baixa, facial, data_inici, usuari, self.photo_data, activities_str)
            cursor.execute(query, values)

            conn.commit()
            messagebox.showinfo("Èxit", "Soci afegit correctament!")
            self.clear_form()  # Limpiar el formulario después de insertar los datos
            cursor.close()
            conn.close()

        except mysql.connector.Error as err:
            messagebox.showerror("Error de base de dades", f"Error al inserir el soci: {err}")

    def convert_date(self, date_str):
        try:
            return datetime.strptime(date_str, "%d-%m-%Y").strftime("%Y-%m-%d")
        except ValueError:
            return None

if __name__ == "__main__":
    root = tk.Tk()
    app = GymManagementSystem(root)
    root.mainloop()
