import tkinter as tk
from tkinter import ttk, messagebox
import mysql.connector
import configparser


class ContabilitatApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Gestió Financera - Esporàdics")

        # Leer configuración desde config.ini
        config = configparser.ConfigParser()
        config.read("config.ini")

        try:
            self.conn = mysql.connector.connect(
                host=config["mysql"]["host"],
                user=config["mysql"]["user"],
                password=config["mysql"]["password"],
                database=config["mysql"]["database"]
            )
        except mysql.connector.Error as err:
            messagebox.showerror("Error", f"Error al conectar a la base de datos: {err}")
            root.destroy()
            return

        self.cursor = self.conn.cursor()

        # Variables para los filtros
        self.selected_month = tk.StringVar()
        self.selected_year = tk.StringVar()

        # Variable para mostrar el total global
        self.total_global_var = tk.StringVar(value="Total: 0.00 €")

        # Configuración de la interfaz
        self.setup_ui()

        # Cargar datos iniciales
        self.import_data()  # Importar datos al iniciar
        self.filter_data()

    def setup_ui(self):
        # Estilos
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TLabel", font=("Arial", 12))
        style.configure("TButton", font=("Arial", 12), padding=5)
        style.configure("Treeview", font=("Arial", 11), rowheight=25)
        style.configure("Treeview.Heading", font=("Arial", 12, "bold"))

        main_frame = ttk.Frame(self.root, padding=10)
        main_frame.pack(fill="both", expand=True)

        header_frame = ttk.Frame(main_frame)
        header_frame.pack(fill="x", pady=5)

        # Filtros
        filter_frame = ttk.Frame(main_frame, padding=10)
        filter_frame.pack(fill="x", pady=10)

        ttk.Label(filter_frame, text="Mes:").grid(row=0, column=0, padx=5, sticky="w")
        months = [str(i) for i in range(1, 13)]
        month_menu = ttk.Combobox(
            filter_frame, 
            textvariable=self.selected_month, 
            values=["Tots"] + months, 
            state="readonly", 
            width=10
        )
        month_menu.grid(row=0, column=1, padx=5)
        month_menu.current(0)

        ttk.Label(filter_frame, text="Any:").grid(row=0, column=2, padx=5, sticky="w")
        years = self.get_years()
        year_menu = ttk.Combobox(
            filter_frame, 
            textvariable=self.selected_year, 
            values=["Tots"] + years, 
            state="readonly", 
            width=10
        )
        year_menu.grid(row=0, column=3, padx=5)
        year_menu.current(0)

        filter_button = ttk.Button(filter_frame, text="Filtrar", command=self.filter_data)
        filter_button.grid(row=0, column=4, padx=5)

        # Total global
        total_frame = ttk.Frame(main_frame, padding=5)
        total_frame.pack(fill="x", pady=10)

        self.total_label = tk.Label(
            total_frame, 
            textvariable=self.total_global_var, 
            font=("Arial", 14, "bold"), 
            fg="red", 
            anchor="center"
        )
        self.total_label.pack()

        # Tabla para mostrar datos
        table_frame = ttk.Frame(main_frame)
        table_frame.pack(fill="both", expand=True, pady=10)

        columns = ("nom", "mes", "any", "total")
        self.tree = ttk.Treeview(
            table_frame, columns=columns, show="headings", selectmode="browse"
        )
        self.tree.heading("nom", text="Nom")
        self.tree.heading("mes", text="Mes")
        self.tree.heading("any", text="Any")
        self.tree.heading("total", text="Total (€)")
        self.tree.column("nom", width=200, anchor="w")
        self.tree.column("mes", width=100, anchor="center")
        self.tree.column("any", width=100, anchor="center")
        self.tree.column("total", width=150, anchor="e")

        scroll_y = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscroll=scroll_y.set)
        self.tree.pack(side="left", fill="both", expand=True)
        scroll_y.pack(side="right", fill="y")

    def get_years(self):
        self.cursor.execute("SELECT DISTINCT YEAR(Alta) FROM esporadics ORDER BY YEAR(Alta) DESC")
        return [str(year[0]) for year in self.cursor.fetchall()]

    def import_data(self):
        self.cursor.execute("SELECT nom, MONTH(Alta) AS mes, YEAR(Alta) AS any, SUM(quantitat) AS total FROM esporadics GROUP BY nom, mes, any")
        self.data = self.cursor.fetchall()
        self.update_treeview()

    def filter_data(self):
        month = self.selected_month.get()
        year = self.selected_year.get()
        conditions = []
        params = []

        if month != "Tots":
            conditions.append("MONTH(Alta) = %s")
            params.append(month)
        if year != "Tots":
            conditions.append("YEAR(Alta) = %s")
            params.append(year)

        query = "SELECT nom, MONTH(Alta) AS mes, YEAR(Alta) AS any, SUM(quantitat) AS total FROM esporadics"
        if conditions:
            query += " WHERE " + " AND ".join(conditions)
        query += " GROUP BY nom, mes, any"

        self.cursor.execute(query, params)
        self.data = self.cursor.fetchall()
        self.update_treeview()

    def update_treeview(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        total_global = 0
        for row in self.data:
            self.tree.insert("", "end", values=row)
            total_global += row[3]  # Sumar el total

        self.total_global_var.set(f"Total: {total_global:.2f} €")

    def on_closing(self):
        self.cursor.close()
        self.conn.close()
        self.root.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = ContabilitatApp(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()
