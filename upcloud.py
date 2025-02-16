import pyodbc
from datetime import datetime

#import mysql.connector

# 📌 Configuración de la conexión a Access
access_conn_str = (
    "DRIVER={Microsoft Access Driver (*.mdb, *.accdb)};"
    "DBQ=D:\\INFORMECIERRE\\PCHIA\\PASTAIO.mdb;"
    "PWD=;"  # Si hay contraseña, colócala aquí
)

# 📌 Configuración de la conexión a MySQL
mysql_conn_str = (
    "DRIVER={MySQL ODBC 9.2 ANSI Driver};"
    "SERVER=127.0.0.1;PORT=3306;"
    "DATABASE=laravel;"
    "USER=root;PASSWORD=;"
    "OPTION=3;"
)
try:
    # Conectar a Access y MySQL
    access_conn = pyodbc.connect(access_conn_str)
    mysql_conn = pyodbc.connect(mysql_conn_str)

    access_cursor = access_conn.cursor()
    mysql_cursor = mysql_conn.cursor()

    # **3️⃣ Diccionario de Queries**
    queries = {
        "JobTitles": "SELECT jobtitletext, jobtitleinactive, defaultsecuritylevel FROM JobTitles ORDER BY JobtitleID",
        "EmployeeFiles": "SELECT firstname, lastname, jobtitleid, securitylevel,accesscode,employeeinactive FROM EmployeeFiles ORDER BY EmployeeID",
        "MenuCategories": "SELECT menucategorytext, menucategoryinactive FROM MenuCategories ORDER BY MenuCategoryID",
        "MenuGroups": "SELECT menugrouptext, menugroupinactive, displayindex FROM MenuGroups ORDER BY MenuGroupID",
        #"MenuItems": "SELECT menucategorytext, menucategoryinactive FROM MenuCategories",
    }

    # **4️⃣ Diccionario de INSERTS**
    inserts = {
        "JobTitles": "INSERT INTO JobTitles (jobtitletext, jobtitleinactive,defaultsecuritylevel, created_at,updated_at) VALUES (?, ?, ?,NOW(),NOW())",
        "EmployeeFiles": "INSERT INTO EmployeeFiles (firstname, lastname, jobtitleid, securitylevel,accesscode,employeeinactive,created_at,updated_at) VALUES (?, ?, ?, ?, ?, ?,NOW(),NOW())",
        "MenuCategories": "INSERT INTO Categories (menucategorytext, menucategoryinactive,created_at,updated_at) VALUES (?, ?,NOW(),NOW())",
        "MenuGroups": "INSERT INTO Groups (menugrouptext, menugroupinactive, displayindex,created_at,updated_at) VALUES (?, ?, ?,NOW(),NOW())",
    }

    # **5️⃣ Definir columnas booleanas por tabla**
    boolean_columns = {
        "JobTitles": [1],  # Tercera columna (jobtitleinactive) es booleana
        "EmployeeFiles": [5],  # Tercera y cuarta columnas (is_active, is_manager) son booleanas
        "MenuCategories": [1],
        "MenuGroups": [1],
    }

    # **6️⃣ Función para convertir booleanos**
    def convert_boolean(value):
        return 1 if value == True else 0

    # **7️⃣ Procesar cada tabla y convertir los datos**
    for table, query in queries.items():
        access_cursor.execute(query)
        rows = access_cursor.fetchall()
        try:
            print(f"🔄 Procesando {table}...")
            # 🔹 Iniciar transacción en Access
            mysql_cursor.execute("START TRANSACTION")
            converted_rows = []
            for row in rows:
                #print(row)
                new_row = list(row)  # Convertimos la tupla a lista para modificar valores

                # Convertir solo las columnas booleanas definidas para esta tabla
                for index in boolean_columns.get(table, []):
                    new_row[index] = convert_boolean(new_row[index])

                converted_rows.append(tuple(new_row))  # Convertir de nuevo a tupla
            # 🔹 Insertar en MySQL
            if converted_rows:
                mysql_cursor.executemany(inserts[table], converted_rows)
                print(f"✅ Insertados {len(rows)} registros en {table}")

            # 🔹 Confirmar transacción en Access
            mysql_cursor.commit()
        except Exception as e:
            # 🔴 Rollback SOLO en la tabla actual
            access_conn.rollback()
            print(f"❌ Error en {table}: {e}")
            # # **8️⃣ Insertar en MySQL**
            # if converted_rows:
            #     mysql_cursor.executemany(inserts[table], converted_rows)
            #     print(f"✅ Insertados {len(rows)} registros en {table}")
            # 🔹 **Actualizar synchver**
        try:
            tables = {
                "JobTitles": {"mysql_table": "JobTitles", "mysql_key": "id", "access_table": "JobTitles", "access_key": "jobtitleid"},
                "MenuCategories": {"mysql_table": "Categories", "mysql_key": "id", "access_table": "MenuCategories", "access_key": "menucategoryid"},
                "MenuGroups": {"mysql_table": "Categories", "mysql_key": "id", "access_table": "MenuGroups", "access_key": "menugroupid"},
                "EmployeeFiles": {"mysql_table": "EmployeeFiles", "mysql_key": "id", "access_table": "EmployeeFiles", "access_key": "employeeid"},
                "EmployeeTimeCards": {"mysql_table": "timecards", "mysql_key": "id", "access_table": "EmployeeTimeCards", "access_key": "employeeid"},
            }


            for table_name, mapping in tables.items():
                mysql_table = mapping["mysql_table"]
                mysql_key = mapping["mysql_key"]
                access_table = mapping["access_table"]
                access_key = mapping["access_key"]

                # 🔹 Obtener update_at desde MySQL
                mysql_cursor.execute(f"SELECT {mysql_key}, updated_at FROM {mysql_table}")
                mysql_rows = mysql_cursor.fetchall()
                #print(f"Datos obtenidos de {mysql_table}: {mysql_rows}")

                # 🔹 Actualizar synchver en Access con formato correcto
                for record_id, updated_at in mysql_rows:
                    if updated_at:  # Asegurar que el campo no es NULL
                        updated_at_formatted = datetime.strptime(str(updated_at), "%Y-%m-%d %H:%M:%S").strftime("%m/%d/%Y %I:%M:%S %p")
                        #print(updated_at_formatted)
                        QUERY= (f"UPDATE {access_table} SET synchver = #{updated_at_formatted}# WHERE {access_key} = {record_id}")
                        #print(QUERY)
                        access_cursor.execute(f"UPDATE {access_table} SET synchver = #{updated_at_formatted}# WHERE {access_key} = {record_id}")
                        access_conn.commit()

                # 🔹 Confirmar cambios
                print(f"✅ synchver actualizado en {access_table} en Access con updated_at de {mysql_table} en MySQL")

        except Exception as e:
            # 🔴 Rollback solo de synchver
            access_conn.rollback()
            print(f"❌ Error actualizando synchver en {table}: {e}")
    # **9️⃣ Confirmar cambios y cerrar conexiones**
    mysql_conn.commit()
except pyodbc.Error as e:
    print(f"❌ Error: {e}")
    mysql_conn.rollback()
finally:
    # Cerrar conexiones
    access_cursor.close()
    access_conn.close()
    mysql_cursor.close()
    mysql_conn.close()
    print("✅ Conexiones cerradas.")
print("✅ Migración completada exitosamente.")
