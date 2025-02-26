import tkinter as tk
from tkinter import scrolledtext, messagebox
import os
import sys
import winreg
import pyodbc
from updates2 import updates  # Importa la función
from timecardsup import timecards  # Importa la función
from products import updateproducts # Importa la función
from inserts import insertsdata
import logging

# Configurar logging
logging.basicConfig(
    level=logging.DEBUG,
    filename="logaldelocloud.txt",
    filemode="w",
    format="%(asctime)s | INFO | %(message)s",
    datefmt="%Y-%m-%d %I:%M:%S %p"
)

# Captura de salida estándar para redirigir a la GUI y log
class Logger:
    def __init__(self, text_widget):
        self.text_widget = text_widget

    def write(self, message):
        if message.strip():  # Evitar líneas vacías
            self.text_widget.insert(tk.END, message.strip() + "\n")
            self.text_widget.yview(tk.END)  # Auto-scroll
            self.text_widget.update()
            logging.info(message.strip())

    def flush(self):
        pass  # Necesario para compatibilidad con sys.stdout

def leer_clave_registro():
    try:
        ruta = r"Software\VB and VBA Program Settings\Aldelo For Restaurants\Version 3"
        clave = "Data Source"
        reg = winreg.OpenKey(winreg.HKEY_CURRENT_USER, ruta, 0, winreg.KEY_READ)
        valor, _ = winreg.QueryValueEx(reg, clave)
        winreg.CloseKey(reg)
        return valor
    except FileNotFoundError:
        return "Clave no encontrada"
    except Exception as e:
        return f"Error: {e}"

def dbconn():
    ruta = leer_clave_registro()
    print(f"📌 Ruta de base de datos: {ruta}")
    access_conn = pyodbc.connect(rf'DRIVER={{Microsoft Access Driver (*.mdb, *.accdb)}};DBQ={ruta};')
    access_cursor = access_conn.cursor()

    mysql_conn_str = (
        "DRIVER={MySQL ODBC 9.2 ANSI Driver};"
        "SERVER=solucionesintegralespos.com;PORT=3306;"
        "DATABASE=u344335374_aldeloposnube;"
        "USER=u344335374_aldeoadmin;PASSWORD=Sip66353782;"
        "OPTION=3;"
    )
    mysql_conn = pyodbc.connect(mysql_conn_str)
    mysql_cursor = mysql_conn.cursor()
    return access_conn, access_cursor, mysql_conn, mysql_cursor

def ejecutar_timecards():
    print("🚀 Ejecutando sincronización...")
    try:
        access_conn, access_cursor, mysql_conn, mysql_cursor = dbconn()
        timecards(access_conn, access_cursor, mysql_conn, mysql_cursor)
        print("🎯 Proceso finalizado.")
        print("============================================")
        messagebox.showinfo("Éxito", "Sincronización completada.")
    except Exception as e:
        print(f"❌ Error: {e}")
        messagebox.showerror("Error", f"Error en sincronización: {e}")

def updates_execute():
    print("🚀 Ejecutando actualización...")
    try:
        try:
            access_conn, access_cursor, mysql_conn, mysql_cursor = dbconn()
            updates(access_conn, access_cursor, mysql_conn, mysql_cursor)
            print("🎯 Proceso finalizado.")
        except Exception as e:
            print(f"❌ Error: {e}")
            messagebox.showerror("Error", f"Error en actualización: {e}")
        try:
            access_conn, access_cursor, mysql_conn, mysql_cursor = dbconn()
            updateproducts(access_conn, access_cursor, mysql_conn, mysql_cursor)
            print("🎯 Proceso finalizado.")
        except Exception as e:
            print(f"❌ Error: {e}")
            messagebox.showerror("Error", f"Error en actualización: {e}")
        try:
            access_conn, access_cursor, mysql_conn, mysql_cursor = dbconn()
            insertsdata(access_conn, access_cursor, mysql_conn, mysql_cursor)
            print("🎯 Proceso finalizado.")
            print("============================================")
        except Exception as e:
            print(f"❌ Error: {e}")
            messagebox.showerror("Error", f"Error en actualización: {e}")
        messagebox.showinfo("Éxito", "Actualización completada.")
    except Exception as e:
        print(f"❌ Error: {e}")
        messagebox.showerror("Error", f"Error en actualización: {e}")

# 🏠 Crear ventana principal
root = tk.Tk()
root.title("Aldelo Cloud Connector")
root.geometry("600x500")
root.resizable(False, False)
# Obtener la ruta correcta del ícono
if getattr(sys, 'frozen', False):  # Si el programa está compilado
    path = sys._MEIPASS
else:
    path = os.path.dirname(__file__)
# 🖼️ Logo
icon_path = os.path.abspath("iconreport.ico")
if os.path.exists(icon_path):
    try:
        root.iconbitmap(icon_path)
    except:
        pass  # Si hay un error, simplemente ignorarlo

logo_label = tk.Label(root)
logo_path = os.path.join(path, "logo.png")
if os.path.exists(logo_path):
    try:
        from PIL import Image, ImageTk
        img = Image.open("logo.png").resize((250, 100))
        logo = ImageTk.PhotoImage(img)
        logo_label.config(image=logo)
        logo_label.image = logo
    except Exception as e:
        print(f"❌ Error: {e}")
        messagebox.showerror("Error", f"Error en imagen: {e}")
logo_label.pack(pady=10)

# 📌 Botones
fuente_bold = ("Arial", 10, "bold")
btn_subir = tk.Button(root, text="Subir cambios", command=ejecutar_timecards, width=20, bg="lightblue",font=fuente_bold)
btn_bajar = tk.Button(root, text="Bajar cambios", command=updates_execute, width=20, bg="lightgreen",font=fuente_bold)
btn_subir.pack(pady=5)
btn_bajar.pack(pady=5)

# 📝 Área de log con desplazamiento
log_frame = tk.Frame(root)
log_frame.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)

log_label = tk.Label(log_frame, text="Log de mensajes:", font=("Arial", 10, "bold"))
log_label.pack(anchor="w")

log_area = scrolledtext.ScrolledText(log_frame, width=70, height=15, wrap=tk.WORD)
log_area.pack(fill=tk.BOTH, expand=True)

# Redirigir print al área de log
sys.stdout = Logger(log_area)

# 🏁 Iniciar aplicación
root.mainloop()
