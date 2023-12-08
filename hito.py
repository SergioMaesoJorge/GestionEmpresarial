import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import openpyxl
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import tkinter.simpledialog  # Importa el módulo para obtener la entrada del usuario

class ERPModuleUI:
    def __init__(self, root):
        self.root = root
        self.root.title("ERP Module")

        # Conexión a la base de datos
        self.conn = sqlite3.connect('erp_database.db')
        self.cursor = self.conn.cursor()

        # Crear tablas si no existen
        self.create_tables()

        # Crear interfaz de usuario
        self.create_ui()

    def create_tables(self):
        # Tabla 'producto'
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS producto (
                id INTEGER PRIMARY KEY,
                nombre TEXT,
                stock INTEGER,
                precio REAL
            )
        ''')

        # Commit para guardar cambios
        self.conn.commit()

    def create_ui(self):
        # Menú
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Archivo", menu=file_menu)
        file_menu.add_command(label="Salir", command=self.root.destroy)

        # Botones y elementos de la interfaz
        btn_add_product = tk.Button(self.root, text="Agregar Producto", command=self.add_product)
        btn_add_product.pack()

        btn_show_table = tk.Button(self.root, text="Mostrar Tabla", command=self.show_table)
        btn_show_table.pack()

        btn_export_excel = tk.Button(self.root, text="Exportar a Excel", command=self.export_to_excel)
        btn_export_excel.pack()

        btn_show_graph = tk.Button(self.root, text="Mostrar Gráfico", command=self.show_graph)
        btn_show_graph.pack()

    def add_product(self):
        # Formulario para agregar nuevos productos
        add_product_window = tk.Toplevel(self.root)
        add_product_window.title("Agregar Producto")

        ttk.Label(add_product_window, text="Nombre:").grid(row=0, column=0)
        product_name_entry = ttk.Entry(add_product_window)
        product_name_entry.grid(row=0, column=1)

        ttk.Label(add_product_window, text="Stock:").grid(row=1, column=0)
        stock_entry = ttk.Entry(add_product_window)
        stock_entry.grid(row=1, column=1)

        ttk.Label(add_product_window, text="Precio:").grid(row=2, column=0)
        price_entry = ttk.Entry(add_product_window)
        price_entry.grid(row=2, column=1)

        add_button = ttk.Button(add_product_window, text="Agregar", command=lambda: self.insert_product(
            product_name_entry.get(), stock_entry.get(), price_entry.get(), add_product_window))
        add_button.grid(row=3, column=0, columnspan=2)

    def insert_product(self, name, stock, price, window):
        try:
            stock = int(stock)
            price = float(price)

            self.cursor.execute("INSERT INTO producto (nombre, stock, precio) VALUES (?, ?, ?)", (name, stock, price))
            self.conn.commit()

            messagebox.showinfo("Éxito", "Producto agregado correctamente")

            window.destroy()
        except ValueError:
            messagebox.showerror("Error", "Por favor, ingrese valores válidos para stock y precio.")

    def show_table(self):
        # Mostrar la tabla de productos en una nueva ventana
        table_window = tk.Toplevel(self.root)
        table_window.title("Tabla de Productos")

        self.cursor.execute("SELECT * FROM producto")
        result = self.cursor.fetchall()

        tree = ttk.Treeview(table_window, columns=("ID", "Nombre", "Stock", "Precio"))
        tree.heading("#0", text="ID")
        tree.heading("#1", text="Nombre")
        tree.heading("#2", text="Stock")
        tree.heading("#3", text="Precio")

        for row in result:
            tree.insert("", "end", values=row)

        tree.pack()

    def export_to_excel(self):
        # Exportar la tabla de productos a un archivo Excel
        self.cursor.execute("SELECT * FROM producto")
        result = self.cursor.fetchall()

        wb = openpyxl.Workbook()
        ws = wb.active

        headers = ["ID", "Nombre", "Stock", "Precio"]
        ws.append(headers)

        for row in result:
            ws.append(row)

        wb.save("productos_excel.xlsx")
        messagebox.showinfo("Éxito", "Datos exportados a Excel correctamente")

    def show_graph(self):
        graph_type = tkinter.simpledialog.askstring("Tipo de Gráfico", "Elija el tipo de gráfico (barras, circular, lineas):")

        if graph_type:
            if graph_type.lower() == "barras":
                self.show_bar_chart()
            elif graph_type.lower() == "circular":
                self.show_pie_chart()
            elif graph_type.lower() == "lineas":
                self.show_line_chart()
            else:
                messagebox.showwarning("Advertencia", "Tipo de gráfico no válido. Se mostrará un gráfico de barras por defecto.")
                self.show_bar_chart()
        else:
            messagebox.showwarning("Advertencia", "No se proporcionó un tipo de gráfico. Se mostrará un gráfico de barras por defecto.")
            self.show_bar_chart()

    def show_bar_chart(self):
        self.cursor.execute("SELECT * FROM producto ORDER BY stock DESC")
        result_sorted = self.cursor.fetchall()

        data = [row[2] for row in result_sorted]  # Obtener datos de stock

        fig, ax = plt.subplots()
        ax.bar(range(len(data)), data)
        ax.set_xlabel('ID')
        ax.set_ylabel('Stock')
        ax.set_title('Stock de Productos - Gráfico de Barras')

        canvas = FigureCanvasTkAgg(fig, master=self.root)
        canvas.draw()
        canvas.get_tk_widget().pack()

        plt.show()

    def show_pie_chart(self):
        self.cursor.execute("SELECT * FROM producto")
        result = self.cursor.fetchall()

        labels = [row[1] for row in result]  # Obtener nombres de productos
        sizes = [row[2] for row in result]   # Obtener datos de stock

        fig, ax = plt.subplots()
        ax.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90)
        ax.axis('equal')

        ax.set_title('Stock de Productos - Gráfico Circular')

        canvas = FigureCanvasTkAgg(fig, master=self.root)
        canvas.draw()
        canvas.get_tk_widget().pack()

        plt.show()

    def show_line_chart(self):
        self.cursor.execute("SELECT * FROM producto ORDER BY id")
        result_sorted = self.cursor.fetchall()

        data = [row[3] for row in result_sorted]  # Obtener datos de precios

        fig, ax = plt.subplots()
        ax.plot(range(len(data)), data, marker='o', linestyle='-', color='b')
        ax.set_xlabel('ID')
        ax.set_ylabel('Precio')
        ax.set_title('Precios de Productos - Gráfico de Líneas')

        canvas = FigureCanvasTkAgg(fig, master=self.root)
        canvas.draw()
        canvas.get_tk_widget().pack()

        plt.show()


if __name__ == "__main__":
    root = tk.Tk()
    app = ERPModuleUI(root)
    root.mainloop()
