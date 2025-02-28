import pyodbc
import json
import winreg
from tkinter import messagebox

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
        "SERVER=127.0.0.1;PORT=3306;"
        "DATABASE=laravel;"
        "USER=root;PASSWORD=;"
        "OPTION=3;"
    )
    mysql_conn = pyodbc.connect(mysql_conn_str)
    mysql_cursor = mysql_conn.cursor()
    return access_conn, access_cursor, mysql_conn, mysql_cursor

def audit(access_conn, access_cursor, mysql_conn, mysql_cursor):

    # Cargar configuración y convertir la sucursal a entero
    with open('settings.json', 'r') as c:
        config = json.load(c)
    branch = int(config["sucursal"])

    # Diccionario de queries para obtener datos de MySQL (se generarán dinámicamente)
    # (En este ejemplo, la query no utiliza branch, pues se obtiene la lista completa de IDs)
    queries = {}

    # Mapeo de nombres de tablas entre MySQL y Access
    tables = {
        "JobTitles": {"mysql_table": "jobtitles", "mysql_key": "id", "access_table": "JobTitles", "access_key": "jobtitleid"},
        "MenuCategories": {"mysql_table": "categories", "mysql_key": "id", "access_table": "MenuCategories", "access_key": "menucategoryid"},
        "MenuGroups": {"mysql_table": "groups", "mysql_key": "id", "access_table": "MenuGroups", "access_key": "menugroupid"},
        "EmployeeFiles": {"mysql_table": "employeefiles", "mysql_key": "id", "access_table": "EmployeeFiles", "access_key": "employeeid"},
        "MenuItems": {"mysql_table": "products", "mysql_key": "barcode", "access_table": "MenuItems", "access_key": "barcode"},
    }

    for key, mapping in tables.items():
        mysql_key = mapping['mysql_key']
        mysql_table = mapping['mysql_table']
        queries[key] = f"SELECT `{mysql_key}` FROM `{mysql_table}`"

    # Query para insertar en errorsmdb en MySQL
    insert_query = """
    INSERT INTO errorsmdb (idtable, name, branchid, `table`, sent, created_at, updated_at)
    VALUES (?, ?, ?, ?, ?, NOW(), NOW())
    """

    # Query para validar si ya existe el error para hoy
    select_query = """
    SELECT COUNT(*) FROM errorsmdb
    WHERE idtable = ? AND branchid = ? AND `table` = ? AND DATE(created_at) = CURDATE()
    """

    try:
        for table in tables.keys():
            print(f"🔄 Procesando {table}...")

            # Ejecutar la query de MySQL
            query = queries[table]  # En este ejemplo, no se formatea branch
            mysql_cursor.execute(query)
            if table == "MenuItems":
                mysql_ids = {str(row[0]).strip().upper() for row in mysql_cursor.fetchall()}
            else:
                mysql_ids = {row[0] for row in mysql_cursor.fetchall()}

            # Obtener datos de Access
            access_table_name = tables[table]['access_table']
            access_cursor.execute(f"SELECT * FROM {access_table_name}")
            access_data = access_cursor.fetchall()
            sent = False
            # Insertar en errorsmdb los registros de Access que NO están en MySQL
            for access_row in access_data:
                # Para MenuItems, se normaliza el barcode (se asume que se encuentra en la columna 26, índice 25)
                if table == "MenuItems":
                    access_id = str(access_row[25]).strip().upper()
                else:
                    access_id = access_row[0]

                if access_id not in mysql_ids:
                    # Verificar si ya existe un error para este idtable, branch y table hoy
                    mysql_cursor.execute(select_query, (str(access_id), branch, access_table_name))
                    exists = mysql_cursor.fetchone()[0]
                    if exists:
                        # print(f"✅ Registro de error ya existe para {table} con id {access_id} y branch {branch} hoy. Se omite inserción.")
                        continue

                    # Se asume que el nombre está en la segunda columna (índice 1) del select de Access
                    error_params = (str(access_id), access_row[1], branch, access_table_name, sent)
                    mysql_cursor.execute(insert_query, error_params)
                    print(f"⚠️ Insertado error en errorsmdb para {table} con id {access_id}")

            mysql_conn.commit()
            print(f"✅ Procesamiento completado para {table}")

        print("✅ Sincronización finalizada.")

    except pyodbc.Error as e:
        mysql_conn.rollback()
        print(f"❌ Error general: {e}")
        messagebox.showerror("Error", f"❌ Error general: {e}")

    finally:
        access_cursor.close()
        access_conn.close()
        mysql_cursor.close()
        mysql_conn.close()
        print("✅ Conexiones cerradas.")
        print("✅ Proceso terminado.")

    return "✅ Auditoria completada exitosamente."

def updatep():
    access_conn, access_cursor, mysql_conn, mysql_cursor = dbconn()
    audit(access_conn, access_cursor, mysql_conn, mysql_cursor)

updatep()
print("============================================")
