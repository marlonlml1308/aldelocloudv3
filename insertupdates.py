import pyodbc
from datetime import datetime

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

    # Diccionario de queries para obtener datos de Mysql
    queries = {
        "JobTitles": "SELECT jobtitleid, jobtitletext, jobtitleinactive, updated_at FROM JobTitles",
        #"EmployeeFiles": "SELECT id, firstname, lastname, jobtitleid, securitylevel, accesscode, employeeinactive, updated_at FROM EmployeeFiles",
        "MenuCategories": "SELECT id, menucategorytext, menucategoryinactive, updated_at FROM Categories",
        "MenuGroups": "SELECT id, menugrouptext, menugroupinactive, displayindex, updated_at FROM Groups",
    }

    # Diccionario de queries de actualización para Access
    updates = {
        "JobTitles": "UPDATE JobTitles SET jobtitletext=?, jobtitleinactive=?, synchver=? WHERE jobtitleid=?",
        #"EmployeeFiles": "UPDATE EmployeeFiles SET firstname=?, lastname=?, jobtitleid=?, securitylevel=?, accesscode=?, employeeinactive=?, synchver=? WHERE employeeid=?",
        "MenuCategories": "UPDATE MenuCategories SET menucategorytext=?, menucategoryinactive=?, synchver=? WHERE menucategoryid=?",
        "MenuGroups": "UPDATE MenuGroups SET menugrouptext=?, menugroupinactive=?, displayindex=?, synchver=? WHERE menugroupid=?",
    }

    # Mapeo de nombres de tablas entre MySQL y Access
    tables = {
        "JobTitles": {"mysql_table": "JobTitles", "mysql_key": "id", "access_table": "JobTitles", "access_key": "jobtitleid"},
        "MenuCategories": {"mysql_table": "categories", "mysql_key": "id", "access_table": "MenuCategories", "access_key": "menucategoryid"},
        "MenuGroups": {"mysql_table": "groups", "mysql_key": "id", "access_table": "MenuGroups", "access_key": "menugroupid"},
        #"EmployeeFiles": {"mysql_table": "EmployeeFiles", "mysql_key": "id", "access_table": "EmployeeFiles", "access_key": "employeeid"},
    }

        # **5️⃣ Definir columnas booleanas por tabla**
    boolean_columns = {
        "JobTitles": [1],  # Tercera columna (jobtitleinactive) es booleana
        "EmployeeFiles": [5],  # Tercera y cuarta columnas (is_active, is_manager) son booleanas
        "MenuCategories": [1],
        "MenuGroups": [1],
    }

    # Función para convertir booleanos
    def convert_boolean(value):
        return 1 if value else 0

    # 🔄 Sincronización de datos
    for table in ["MenuCategories", "MenuGroups", "JobTitles"]:
        print(f"🔄 Sincronizando {table}...")

        # 🔹 Obtener nombres de columnas en Access
        access_cursor.execute(f"SELECT top 1 * FROM {table}")
        column_names = [desc[0] for desc in access_cursor.description]  # Lista con los nombres de columnas

        # 🔹 Obtener datos de Access
        print(f"SELECT * FROM {table}")
        access_cursor.execute(f"SELECT * FROM {table}")
        access_data = {row[0]: row for row in access_cursor.fetchall()}  # Diccionario con la PK como clave

        # 🔹 Obtener datos de MySQL
        mysql_table = tables[table]["mysql_table"]
        mysql_key = tables[table]["mysql_key"]
        mysql_cursor.execute(queries[table])
        mysql_data = mysql_cursor.fetchall()

        updated_ids = []  # Lista para almacenar los registros que se actualizarán
        print(f"🔍 Registros obtenidos de MySQL ({mysql_table}): {len(mysql_data)}")
        # 🔹 Comparar y actualizar registros
        for row in mysql_data:
            primary_key = row[0]  # Primera columna como clave primaria
            updated_at = row[-1]  # Última columna debe ser updated_at en MySQL
            new_data = list(row)  # Convertimos la tupla en lista para modificar

            # Convertir booleanos si es necesario
            for index in boolean_columns.get(table, []):
                new_data[index] = convert_boolean(new_data[index])
                    # 🔹 Convertir `updated_at` a formato Access (MM/DD/YYYY HH:MM:SS AM/PM)
            if isinstance(updated_at, datetime):
                updated_at_access = f"#{updated_at.strftime('%m/%d/%Y %I:%M:%S %p')}#"
            else:
                updated_at_access = None
            # 🔹 Obtener `synchver` si existe en Access
            if primary_key in access_data:
                access_row = access_data[primary_key]

                if "SynchVer" in column_names:
                    synchver_index = column_names.index("SynchVer")
                    synchver = access_row[synchver_index]  # Obtener synchver en la posición correcta

                    # 🔹 Verificar si `synchver` es una fecha válida antes de convertirla
                    try:
                         # 🔹 Verificar si synchver es una fecha válida antes de convertirla
                        if isinstance(synchver, str):
                            try:
                                synchver = datetime.strptime(synchver, "%m/%d/%Y %I:%M:%S %p")  # Formato en Access
                            except ValueError:
                                print(f"⚠️ Error al convertir SynchVer: {synchver}")
                             # Saltar esta iteración si la conversión falla

                        # 🔹 Convertir updated_at si es string
                        # if isinstance(updated_at, str):
                        #     try:
                        #         updated_at = datetime.strptime(updated_at, "%Y-%m-%d %H:%M:%S")
                        #     except ValueError:
                        #         print(f"⚠️ Error al convertir updated_at: {updated_at}")
                        #         continue  # Saltar si la conversión falla
                        # if isinstance(synchver, str):
                        #     synchver = datetime.strptime(synchver, "%m/%d/%Y %I:%M:%S %p").strftime("%m/%d/%Y %I:%M:%S %p")  # Formato en Access
                        # 🔹 Comparar solo si ambas son fechas válidas
                        # if isinstance(updated_at, datetime) and isinstance(synchver, datetime) and updated_at > synchver:
                        if isinstance(updated_at, datetime) and isinstance(synchver, datetime) and updated_at > synchver:
                            print(f"🔄 Comparando: {updated_at} > {synchver}")
                            update_query = updates[table]
                            new_data = list(row)[1:]
                            # 🔹 Convertir synchver a string antes del UPDATE en Access
                            new_data[-1] = updated_at.strftime("#%m/%d/%Y %I:%M:%S %p#")
                            new_data.append(primary_key)
                            # print(f"🔍 QUERY: {update_query}")
                            # print(f"🔍 DATOS: {new_data}")
                            # print(f"🔍 TOTAL DE PARÁMETROS ESPERADOS: {update_query.count('?')}")
                            # print(f"🔍 TOTAL DE PARÁMETROS ENVIADOS: {len(new_data)}")
                            # access_cursor.execute(update_query, new_data)
                            # print(f"🔄 Actualizado {table}: {primary_key}")
                            # 🔍 Construir y mostrar la consulta con valores interpolados
                            # 🔍 Construir y mostrar la consulta con valores interpolados
                            query_with_values = update_query
                            for value in new_data:
                                if isinstance(value, str):
                                    query_with_values = query_with_values.replace("?", f"'{value}'", 1)
                                elif isinstance(value, datetime):
                                    query_with_values = query_with_values.replace("?", value.strftime("#%m/%d/%Y %I:%M:%S %p#"), 1)
                                else:
                                    query_with_values = query_with_values.replace("?", str(value), 1)

                            print(f"🔍 QUERY EJECUTADA: {query_with_values}")

                            # 🔹 Ejecutar actualización en Access
                            access_cursor.execute(update_query, new_data)
                            # 🔹 Confirmar cambios en Access
                            access_conn.commit()
                            print(f"✅ synchver actualizado en {tables[table]['access_table']} en Access con updated_at de {mysql_table} en MySQL")
                    except ValueError:
                        print(f"⚠️ Error: synchver inválido en {table}, ID {primary_key}: {synchver}")
            else:
                # 🔹 Insertar nuevo registro si `synchver` no existe en Access
                # insert_query = inserts[table]
                # access_cursor.execute(insert_query, new_data)
                access_conn.commit()
                print(f"✅ Insertado nuevo en {table}: {primary_key}")


    # **Confirmar cambios y cerrar conexiones**
    access_conn.commit()
except pyodbc.Error as e:
    print(f"❌ Error: {e}")
    access_conn.rollback()
finally:
    # Cerrar conexiones
    access_cursor.close()
    access_conn.close()
    mysql_cursor.close()
    mysql_conn.close()
    print("✅ Conexiones cerradas.")

print("✅ Migración completada exitosamente.")
