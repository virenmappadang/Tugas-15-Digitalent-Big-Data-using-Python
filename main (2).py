import tkinter as tk
from tkinter import StringVar, messagebox
from tkinter import ttk
from tkinter import Frame, Label, Entry, Button
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import pymysql
import tkcalendar as tkc  # Add tkcalendar for date selection

def connect_to_database():
    return pymysql.connect(
        host="localhost",
        user="root",
        password="",  # Replace with your MySQL password
        database="employee_performa"
    )

def create_employee(tanggal, nama_karyawan, jenis_kelamin, lama_kerja, gaji_pokok, jumlah_produk, jumlah_insentif):
    connection = connect_to_database()
    cursor = connection.cursor()
    cursor.execute(
        "INSERT INTO employee_performa_grafik (tanggal, nama_karyawan, jenis_kelamin, lama_kerja, gaji_pokok, jumlah_produk_yang_terjual, jumlah_insentif) VALUES (%s, %s, %s, %s, %s, %s, %s)",
        (tanggal, nama_karyawan, jenis_kelamin, lama_kerja, gaji_pokok, jumlah_produk, jumlah_insentif)
    )
    connection.commit()
    connection.close()

def read_employees():
    connection = connect_to_database()
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM employee_performa_grafik")
    employees = cursor.fetchall()
    connection.close()
    return employees

def update_employee(id, tanggal, nama_karyawan, jenis_kelamin, lama_kerja, gaji_pokok, jumlah_produk, jumlah_insentif):
    connection = connect_to_database()
    cursor = connection.cursor()
    cursor.execute(
        "UPDATE employee_performa_grafik SET tanggal=%s, nama_karyawan=%s, jenis_kelamin=%s, lama_kerja=%s, gaji_pokok=%s, jumlah_produk_yang_terjual=%s, jumlah_insentif=%s WHERE id=%s",
        (tanggal, nama_karyawan, jenis_kelamin, lama_kerja, gaji_pokok, jumlah_produk, jumlah_insentif, id)
    )
    connection.commit()
    connection.close()

def delete_employee(id):
    connection = connect_to_database()
    cursor = connection.cursor()
    cursor.execute("DELETE FROM employee_performa_grafik WHERE id=%s", (id,))
    connection.commit()
    connection.close()

def fetch_employee(id):
    connection = connect_to_database()
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM employee_performa_grafik WHERE id=%s", (id,))
    employee = cursor.fetchone()
    connection.close()
    return employee

class SampleApp(tk.Tk):
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        self.title("BonusBuzz Tracker")
        self.title_font = tk.font.Font(family='Helvetica', size=18, weight="bold", slant="italic")

        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(1, weight=1)

        frm_buttons = tk.Frame(container, relief=tk.RAISED, bd=2)

        btn_page_primary = tk.Button(frm_buttons, text="Beranda", command=lambda: self.show_frame("StartPage"))
        btn_page_1 = tk.Button(frm_buttons, text="Input Data", command=lambda: self.show_frame("PageOne"))
        btn_page_2 = tk.Button(frm_buttons, text="Data Karyawan", command=lambda: self.show_frame("PageTwo"))
        btn_page_3 = tk.Button(frm_buttons, text="Statistik", command=lambda: self.show_frame("PageThree"))

        self.frames = {}
        for F in (StartPage, PageOne, PageTwo, PageThree):
            page_name = F.__name__
            frame = F(parent=container, controller=self)
            self.frames[page_name] = frame
            frame.grid(row=0, column=1, sticky="nsew")

        btn_page_primary.grid(row=0, column=0, sticky="ew", padx=5, pady=5)
        btn_page_1.grid(row=1, column=0, sticky="ew", padx=5, pady=5)
        btn_page_2.grid(row=2, column=0, sticky="ew", padx=5, pady=5)
        btn_page_3.grid(row=3, column=0, sticky="ew", padx=5, pady=5)

        frm_buttons.grid(row=0, column=0, sticky="ns")

        self.show_frame("StartPage")

    def show_frame(self, page_name):
        frame = self.frames[page_name]
        frame.tkraise()
        if page_name == "StartPage":
            frame.update_summary_plot()
        elif page_name == "PageTwo":
            frame.load_data()
        elif page_name == "PageThree":
            frame.load_employee_names()

class StartPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller

        label = tk.Label(self, text="Beranda", font=controller.title_font)
        label.pack(side="top", fill="x", pady=10)

        self.best_employee_label = tk.Label(self, text="", font=("Helvetica", 14))
        self.best_employee_label.pack(side="top", pady=10)

        self.fig, self.ax = plt.subplots(figsize=(10, 6))
        self.canvas = FigureCanvasTkAgg(self.fig, master=self)
        self.canvas.get_tk_widget().pack(side="top", fill="both", expand=True, padx=10, pady=10)

        self.update_summary_plot()

    def calculate_best_employee(self):
        connection = connect_to_database()
        cursor = connection.cursor()
        cursor.execute("SELECT nama_karyawan, SUM(jumlah_insentif) FROM employee_performa_grafik GROUP BY nama_karyawan")
        employees = cursor.fetchall()
        connection.close()

        employee_dict = {row[0]: row[1] for row in employees}
        best_employee = max(employee_dict, key=employee_dict.get)
        return best_employee, employee_dict[best_employee]

    def update_summary_plot(self):
        connection = connect_to_database()
        cursor = connection.cursor()
        cursor.execute("SELECT nama_karyawan, SUM(jumlah_insentif) FROM employee_performa_grafik GROUP BY nama_karyawan")
        employees = cursor.fetchall()
        connection.close()

        employee_dict = {row[0]: float(row[1]) for row in employees}

        self.ax.clear()
        self.ax.bar(employee_dict.keys(), employee_dict.values(), color='skyblue')
        self.ax.set_title('Ringkasan Performa Karyawan')
        self.ax.set_xlabel('Karyawan')
        self.ax.set_ylabel('Total Insentif')
        self.ax.tick_params(axis='x', rotation=45)

        best_employee, best_incentive = self.calculate_best_employee()
        self.ax.bar(best_employee, best_incentive, color='orange')

        self.best_employee_label.config(text=f'Karyawan Terbaik Bulan Ini: {best_employee} dengan Total Insentif {best_incentive:,.0f}')

        self.canvas.draw()

class PageOne(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        label = tk.Label(self, text="Input Data Karyawan", font=controller.title_font)
        label.pack(side="top", fill="x", pady=10)
        button = tk.Button(self, text="Kembali ke Beranda",
                           command=lambda: controller.show_frame("StartPage"))
        button.pack()

        self.form_frame = Frame(self)
        self.form_frame.grid_rowconfigure(8)
        self.form_frame.grid_columnconfigure(1)

        labels = [
            Label(self.form_frame, text="Tanggal"),
            Label(self.form_frame, text="Nama Karyawan"),
            Label(self.form_frame, text="Jenis Kelamin"),
            Label(self.form_frame, text="Lama Kerja"),
            Label(self.form_frame, text="Gaji Pokok"),
            Label(self.form_frame, text="Jumlah Produk yang Terjual"),
            Label(self.form_frame, text="Jumlah Insentif")
        ]

        self.entries = []
        self.employee_names = ["Aldi Bebaldi", "Begal Khairunnisa", "Luckyman", "Prasbiyanto", "Diluar Nurul", "Virgoun Iskandar", "Wahyu Primarasa"]
        
        for index, label in enumerate(labels):
            label.grid(row=index, column=0)
            if label.cget("text") == "Tanggal":
                entry = tkc.DateEntry(self.form_frame, date_pattern='y-mm-dd')  # Using DateEntry for date
            elif label.cget("text") == "Nama Karyawan":
                self.selected_employee = StringVar(self)
                self.selected_employee.set(self.employee_names[0])  # Default value
                entry = tk.OptionMenu(self.form_frame, self.selected_employee, *self.employee_names, command=self.update_employee_info)
            else:
                entry = tk.Entry(self.form_frame)
                entry.config(state='normal')  # Make sure the entry is editable
                if label.cget("text") == "Jumlah Insentif":
                    entry.config(state='readonly')  # Make it read-only, as it will be calculated

            entry.grid(row=index, column=1)
            self.entries.append(entry)

        # Bind the event to calculate insentif
        self.entries[5].bind("<FocusOut>", self.calculate_insentif)

        self.form_frame.pack()

        save_button = tk.Button(self, text="Simpan Data", command=self.save_data)
        save_button.pack(pady=10)

        self.update_employee_info(self.employee_names[0])  # Initialize with the first employee

    def update_employee_info(self, selected_employee):
        connection = connect_to_database()
        cursor = connection.cursor()
        cursor.execute("SELECT jenis_kelamin, lama_kerja, gaji_pokok FROM employee_performa_grafik WHERE nama_karyawan=%s LIMIT 1", (selected_employee,))
        employee_info = cursor.fetchone()
        connection.close()

        if employee_info:
            jenis_kelamin, lama_kerja, gaji_pokok = employee_info
            self.entries[2].delete(0, tk.END)
            self.entries[2].insert(0, jenis_kelamin)
            self.entries[3].delete(0, tk.END)
            self.entries[3].insert(0, lama_kerja)
            self.entries[4].delete(0, tk.END)
            self.entries[4].insert(0, gaji_pokok)
            self.calculate_insentif()
        else:
            for entry in self.entries[2:5]:
                entry.delete(0, tk.END)
                entry.insert(0, '')

    def calculate_insentif(self, event=None):
        try:
            jumlah_produk = int(self.entries[5].get())
            jumlah_insentif = jumlah_produk * 3000
            self.entries[6].config(state='normal')
            self.entries[6].delete(0, tk.END)
            self.entries[6].insert(0, str(jumlah_insentif))
            self.entries[6].config(state='readonly')
        except ValueError:
            self.entries[6].config(state='normal')
            self.entries[6].delete(0, tk.END)
            self.entries[6].config(state='readonly')

    def save_data(self):
        tanggal = self.entries[0].get()
        nama_karyawan = self.selected_employee.get()
        jenis_kelamin = self.entries[2].get()
        lama_kerja = self.entries[3].get()
        gaji_pokok = self.entries[4].get()
        jumlah_produk = self.entries[5].get()
        jumlah_insentif = self.entries[6].get()

        create_employee(tanggal, nama_karyawan, jenis_kelamin, lama_kerja, gaji_pokok, jumlah_produk, jumlah_insentif)
        messagebox.showinfo("Informasi", "Data karyawan berhasil disimpan")


class PageTwo(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        label = tk.Label(self, text="Data Karyawan", font=controller.title_font)
        label.pack(side="top", fill="x", pady=10)
        button = tk.Button(self, text="Kembali ke Beranda",
                           command=lambda: controller.show_frame("StartPage"))
        button.pack()

        self.tree = ttk.Treeview(self, columns=("ID", "Tanggal", "Nama Karyawan", "Jenis Kelamin", "Lama Kerja", "Gaji Pokok", "Jumlah Produk yang Terjual", "Jumlah Insentif"), show="headings")
        self.tree.heading("ID", text="ID")
        self.tree.heading("Tanggal", text="Tanggal")
        self.tree.heading("Nama Karyawan", text="Nama Karyawan")
        self.tree.heading("Jenis Kelamin", text="Jenis Kelamin")
        self.tree.heading("Lama Kerja", text="Lama Kerja")
        self.tree.heading("Gaji Pokok", text="Gaji Pokok")
        self.tree.heading("Jumlah Produk yang Terjual", text="Jumlah Produk yang Terjual")
        self.tree.heading("Jumlah Insentif", text="Jumlah Insentif")
        self.tree.pack(fill="both", expand=True)

        self.load_data()

        update_button = tk.Button(self, text="Update Data", command=self.update_data)
        update_button.pack(side="left", padx=10, pady=10)

        delete_button = tk.Button(self, text="Delete Data", command=self.delete_data)
        delete_button.pack(side="left", padx=10, pady=10)

    def load_data(self):
        for i in self.tree.get_children():
            self.tree.delete(i)
        employees = read_employees()
        for emp in employees:
            self.tree.insert("", "end", values=emp)

    def update_data(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Peringatan", "Pilih data yang akan diupdate")
            return
        item = self.tree.item(selected_item)
        emp_id = item["values"][0]

        emp_data = fetch_employee(emp_id)
        if emp_data:
            update_window = tk.Toplevel(self)
            update_window.title("Update Data Karyawan")

            labels = ["Tanggal", "Nama Karyawan", "Jenis Kelamin", "Lama Kerja", "Gaji Pokok", "Jumlah Produk yang Terjual", "Jumlah Insentif"]
            entries = []

            for i, label in enumerate(labels):
                tk.Label(update_window, text=label).grid(row=i, column=0)
                if label == "Tanggal":
                    entry = tkc.DateEntry(update_window, date_pattern='y-mm-dd')  # Using DateEntry for date
                    entry.set_date(emp_data[i + 1])
                else:
                    entry = tk.Entry(update_window)
                    entry.insert(0, emp_data[i + 1])
                entry.grid(row=i, column=1)
                entries.append(entry)

            def save_updated_data():
                new_data = [entry.get() for entry in entries]
                update_employee(emp_id, *new_data)
                self.load_data()
                update_window.destroy()
                messagebox.showinfo("Informasi", "Data karyawan berhasil diperbarui")

            tk.Button(update_window, text="Simpan", command=save_updated_data).grid(row=len(labels), column=0, columnspan=2, pady=10)

    def delete_data(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Peringatan", "Pilih data yang akan dihapus")
            return
        item = self.tree.item(selected_item)
        emp_id = item["values"][0]

        if messagebox.askyesno("Konfirmasi", "Apakah Anda yakin ingin menghapus data ini?"):
            delete_employee(emp_id)
            self.load_data()
            messagebox.showinfo("Informasi", "Data karyawan berhasil dihapus")

class PageThree(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        label = tk.Label(self, text="Statistik", font=controller.title_font)
        label.pack(side="top", fill="x", pady=10)
        button = tk.Button(self, text="Kembali ke Beranda",
                           command=lambda: controller.show_frame("StartPage"))
        button.pack()

        self.employee_names = ["Aldi Bebaldi", "Begal Khairunnisa", "Luckyman", "Prasbiyanto", "Diluar Nurul", "Virgoun Iskandar", "Wahyu Primarasa"]
        self.selected_employee = StringVar(self)
        self.selected_employee.set(self.employee_names[0])  # Set the default value
        self.employee_menu = tk.OptionMenu(self, self.selected_employee, *self.employee_names)
        self.employee_menu.pack(pady=10)

        self.selected_month = tkc.DateEntry(self, date_pattern='y-mm-dd', showweeknumbers=False)
        self.selected_month.pack(pady=10)

        show_button = tk.Button(self, text="Tampilkan Statistik", command=self.show_statistics)
        show_button.pack(pady=10)

        self.fig, self.ax = plt.subplots(figsize=(10, 6))
        self.canvas = FigureCanvasTkAgg(self.fig, master=self)
        self.canvas.get_tk_widget().pack(side="top", fill="both", expand=True, padx=10, pady=10)

    def show_statistics(self):
        employee_name = self.selected_employee.get()
        selected_month = self.selected_month.get_date()

        if not employee_name:
            messagebox.showwarning("Peringatan", "Pilih karyawan terlebih dahulu")
            return

        connection = connect_to_database()
        cursor = connection.cursor()
        
        # Query for getting insentif data for the selected employee and month
        cursor.execute("""
            SELECT DAY(tanggal) AS day, SUM(jumlah_insentif) AS insentif
            FROM employee_performa_grafik
            WHERE nama_karyawan=%s AND MONTH(tanggal)=%s AND YEAR(tanggal)=%s
            GROUP BY DAY(tanggal)
            ORDER BY DAY(tanggal)
        """, (employee_name, selected_month.month, selected_month.year))
        data = cursor.fetchall()
        connection.close()

        # Prepare data for plotting
        days = list(range(1, 32))  # Days from 1 to 31
        incentives = [0] * 31  # Initialize with 0

        for day, insentif in data:
            incentives[day - 1] = insentif

        self.ax.clear()
        self.ax.plot(days, incentives, marker='o', linestyle='-', color='b')
        self.ax.set_title(f'Statistik Insentif Harian untuk {employee_name} pada Bulan {selected_month.strftime("%B %Y")}')
        self.ax.set_xlabel('Tanggal')
        self.ax.set_ylabel('Jumlah Insentif')
        self.ax.set_xticks(days)
        self.ax.set_xticklabels([str(day) for day in days], rotation=90)
        self.ax.grid(True)

        self.canvas.draw()


if __name__ == "__main__":
    app = SampleApp()
    app.mainloop()
