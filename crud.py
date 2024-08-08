import mysql.connector

def connect_to_db():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="employee"
    )

def create_sale(nama_karyawan, jenis_kelamin, lama_kerja, gaji_pokok, jumlah_produk_yang_terjual, jumlah_insentif):
    db = connect_to_db()
    cursor = db.cursor()
    cursor.execute("INSERT INTO employee_performa_grafik (nama_karyawan, jenis_kelamin, lama_kerja, gaji_pokok, jumlah_produk_yang_terjual, jumlah_insentif) VALUES (%s, %s, %s, %s, %s, %s)", (nama_karyawan, jenis_kelamin, lama_kerja, gaji_pokok, jumlah_produk_yang_terjual, jumlah_insentif))
    db.commit()
    cursor.close()
    db.close()

def read_sales():
    db = connect_to_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM employee_performa_grafik")
    results = cursor.fetchall()
    cursor.close()
    db.close()
    return results

def update_sale(id, nama_karyawan, jenis_kelamin, lama_kerja, gaji_pokok, jumlah_produk_yang_terjual, jumlah_insentif):
    db = connect_to_db()
    cursor = db.cursor()
    cursor.execute("UPDATE employee_performa_grafik SET nama_karyawan=%s, jenis_kelamin=%s, lama_kerja=%s, gaji_pokok=%s, jumlah_produk_yang_terjual=%s, jumlah_insentif=%s WHERE id=%s", (nama_karyawan, jenis_kelamin, lama_kerja, gaji_pokok, jumlah_produk_yang_terjual, jumlah_insentif, id))
    db.commit()
    cursor.close()
    db.close()

def delete_sale(id):
    db = connect_to_db()
    cursor = db.cursor()
    cursor.execute("DELETE FROM employee_performa_grafik WHERE id=%s", (id,))
    db.commit()
    cursor.close()
    db.close()
