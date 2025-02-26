import pyodbc
from datetime import datetime
from tkinter import messagebox

# 📌 Configuración de la conexión a Access
# access_conn_str = (
#     "DRIVER={Microsoft Access Driver (*.mdb, *.accdb)};"
#     "DBQ=D:\\INFORMECIERRE\\PCHIA\\PASTAIO.mdb;"
#     "PWD=;"  # Si hay contraseña, colócala aquí
# )

# # 📌 Configuración de la conexión a MySQL
# mysql_conn_str = (
#     "DRIVER={MySQL ODBC 9.2 ANSI Driver};"
#     "SERVER=127.0.0.1;PORT=3306;"
#     "DATABASE=laravel;"
#     "USER=root;PASSWORD=;"
#     "OPTION=3;"
# )
def updates(access_conn, access_cursor, mysql_conn, mysql_cursor):
    # 📌 Diccionario de queries para obtener datos de MySQL
    queries = {
        "JobTitles": "SELECT id, jobtitletext, jobtitleinactive,defaultsecuritylevel, updated_at FROM jobtitles",
        "MenuCategories": "SELECT id, menucategorytext, menucategoryinactive, updated_at FROM categories",
        "MenuGroups": "SELECT id, menugrouptext, menugroupinactive, displayindex, updated_at FROM groups",
        "EmployeeFiles": "SELECT id, firstname, lastname, jobtitleid, socialsecuritynumber,securitylevel,accesscode,employeeinactive, updated_at FROM employeefiles",
    }

    # 📌 Diccionario de queries de actualización para Access
    updates = {
        "JobTitles": "UPDATE JobTitles SET jobtitletext=?, jobtitleinactive=?,defaultsecuritylevel=?,synchver=CDate(?) WHERE jobtitleid=?",
        "MenuCategories": "UPDATE MenuCategories SET menucategorytext=?, menucategoryinactive=?, synchver=CDate(?) WHERE menucategoryid=?",
        "MenuGroups": "UPDATE MenuGroups SET menugrouptext=?, menugroupinactive=?, displayindex=?, synchver=CDate(?) WHERE menugroupid=?",
        "EmployeeFiles": "UPDATE EmployeeFiles SET firstname=?, lastname=?, jobtitleid=?, socialsecuritynumber=?,securitylevel=?,accesscode=?,employeeinactive=?,synchver=CDate(?) WHERE employeeid=?",
    }

    # 📌 Mapeo de nombres de tablas entre MySQL y Access
    tables = {
        "JobTitles": {"mysql_table": "JobTitles", "mysql_key": "id", "access_table": "JobTitles", "access_key": "jobtitleid"},
        "MenuCategories": {"mysql_table": "categories", "mysql_key": "id", "access_table": "MenuCategories", "access_key": "menucategoryid"},
        "MenuGroups": {"mysql_table": "groups", "mysql_key": "id", "access_table": "MenuGroups", "access_key": "menugroupid"},
        "EmployeeFiles": {"mysql_table": "EmployeeFiles", "mysql_key": "id", "access_table": "EmployeeFiles", "access_key": "employeeid"},
    }

    # **5️⃣ Definir columnas booleanas por tabla**
    boolean_columns = {
        "JobTitles": [2],  # Tercera columna (jobtitleinactive) es booleana
        "EmployeeFiles": [7],  # Tercera y cuarta columnas (is_active, is_manager) son booleanas
        "MenuCategories": [2],
        "MenuGroups": [2],
    }

    # 📌 Función para convertir booleanos a formato Access
    def convert_boolean(value):
        return True if value == 1 else False

    try:
        # 🔹 Conectar a Access y MySQL
        # access_conn = pyodbc.connect(access_conn_str)
        # mysql_conn = pyodbc.connect(mysql_conn_str)

        # access_cursor = access_conn.cursor()
        # mysql_cursor = mysql_conn.cursor()

        # 🔄 **Sincronización de datos**
        for table in ["MenuCategories", "MenuGroups", "JobTitles", "EmployeeFiles"]:
            print(f"🔄 Sincronizando {table}...")

            # 🔹 Obtener datos de MySQL
            mysql_table = tables[table]["mysql_table"]
            mysql_key = tables[table]["mysql_key"]
            mysql_cursor.execute(queries[table])
            mysql_data = mysql_cursor.fetchall()

            # 🔹 Obtener nombres de columnas en Access
            access_cursor.execute(f"SELECT TOP 1 * FROM {table}")
            column_names = [desc[0] for desc in access_cursor.description]

            # 🔹 Obtener datos de Access
            access_cursor.execute(f"SELECT * FROM {table}")
            access_data = {row[0]: row for row in access_cursor.fetchall()}  # Diccionario con la PK como clave

            try:
                access_conn.autocommit = False  # **Iniciar transacción por tabla**

                for row in mysql_data:
                    primary_key = row[0]  # Primera columna como clave primaria
                    updated_at = row[-1]  # Última columna debe ser updated_at en MySQL
                    new_data = list(row)
                    # 🔹 Convertir booleanos si es necesario
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
                            synchver = access_row[synchver_index]

                            # 🔹 Verificar si `synchver` es una fecha válida antes de convertirla
                            if isinstance(synchver, str):
                                try:
                                    synchver = datetime.strptime(synchver, "%m/%d/%Y %I:%M:%S %p")
                                except ValueError:
                                    print(f"⚠️ Error al convertir SynchVer: {synchver}")
                                    continue  # Saltar esta iteración si la conversión falla

                            # 🔹 Comparar fechas y actualizar si es necesario
                            if isinstance(updated_at, datetime) and isinstance(synchver, datetime) and updated_at > synchver:
                                # print(f"🔄 Actualizando {table} -> {primary_key}: {updated_at} > {synchver}")
                                update_query = updates[table]
                                print('update',updated_at)
                                #new_data = list(row)[1:]  # Omitimos la PK en el set de valores
                                # updated_at_formatted = updated_at.strftime("#%m/%d/%Y %I:%M:%S %p#")  # Formato Access
                                # 🔹 Convertir `updated_at` a objeto `datetime` si aún no lo es
                                # if isinstance(updated_at_formatted, str):
                                #     try:
                                #         updated_at = datetime.strptime(updated_at_formatted, "%m/%d/%Y %I:%M:%S %p")
                                #     except ValueError:
                                #         print(f"⚠️ Error al convertir fecha: {updated_at_formatted}")
                                #         continue
                                # Insertar `updated_at` en la penúltima posición
                                new_data[-1] = updated_at

                                # Mover el `primary_key` al final sin sobrescribirlo
                                new_data.append(new_data.pop(0))
                                                            # print(f"🔍 QUERY: {update_query}")
                                print(f"🔍 DATOS: {new_data}")
                                # print(f"🔍 TOTAL DE PARÁMETROS ESPERADOS: {update_query.count('?')}")
                                # print(f"🔍 TOTAL DE PARÁMETROS ENVIADOS: {len(new_data)}")
                                # Convertir valores a sus tipos correctos antes de ejecutar la consulta
                                # 🔹 Convertir valores numéricos correctamente
                                for i, value in enumerate(new_data):
                                    if isinstance(value, bool):
                                        new_data[i] = value  # Mantener True/False
                                    elif isinstance(value, (int, float)):
                                        continue  # Ya están en el formato correcto
                                    elif isinstance(value, str) and value.isdigit():
                                        new_data[i] = int(value)  # Convertir texto numérico a int
                                    elif isinstance(value, str) and value.replace(".", "", 1).isdigit():
                                        new_data[i] = float(value)  # Convertir texto decimal a float

                                # 🔹 Convertir a tupla (Access requiere una secuencia de valores)
                                query_params = tuple(new_data)
                                # Reemplaza los '?' en la consulta con los valores reales para depuración
                                update_query_debug = update_query
                                for value in query_params:
                                    update_query_debug = update_query_debug.replace("?", f"'{value}'", 1)

                                # print(f"🔍 QUERY FINAL: {update_query_debug}")
                                access_cursor.execute(update_query, query_params)
                                print(f"🔄 Actualizado {table}: {primary_key}")
                    # 🔹 Confirmar cambios después de procesar todos los registros de la tabla
                access_conn.commit()
                print(f"✅ Cambios confirmados en {table}")

            except Exception as e:
                access_conn.rollback()  # **Hacer rollback solo en la tabla afectada**
                print(f"❌ Error en {table}: {e}")
                messagebox.showerror("Error", f"❌ Error en {table}: {e}")
                print("↩️ Se ha realizado rollback en esta tabla.")

        print("✅ Sincronización finalizada.")

    except pyodbc.Error as e:
        print(f"❌ Error general: {e}")
        messagebox.showerror("Error", f"❌ Error general: {e}")

    finally:
        # 🔹 Cerrar conexiones
        if access_cursor:
            access_cursor.close()
        if access_conn:
            access_conn.close()
        if mysql_cursor:
            mysql_cursor.close()
        if mysql_conn:
            mysql_conn.close()
        print("✅ Conexiones cerradas.")
    return "✅ Migración completada exitosamente."
