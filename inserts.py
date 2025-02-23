import pyodbc
from datetime import datetime

# # 📌 Configuración de la conexión a Access
# access_conn_str = (
#     "DRIVER={Microsoft Access Driver (*.mdb, *.accdb)};"
#     "DBQ=D:\\INFORMECIERRE\\p125\\PASTAIO.mdb;"
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
def insertsdata(access_conn, access_cursor, mysql_conn, mysql_cursor):
    # 📌 Diccionario de queries para obtener datos de MySQL
    queries = {
        "JobTitles": "SELECT id, jobtitletext, jobtitleinactive, defaultsecuritylevel, updated_at,id FROM JobTitles ORDER BY id",
        "MenuCategories": "SELECT id, menucategorytext, menucategoryinactive, updated_at,id FROM Categories ORDER BY id",
        "MenuGroups": "SELECT id, menugrouptext, menugroupinactive, displayindex, updated_at,id FROM Groups ORDER BY id",
        "EmployeeFiles": "SELECT id, firstname, lastname, jobtitleid, securitylevel, accesscode,employeeinactive, updated_at,id FROM EmployeeFiles ORDER BY id",
    }

    # 📌 Diccionario de queries de inserción en Access
    inserts = {
        "JobTitles": "INSERT INTO JobTitles (jobtitleid, jobtitletext, jobtitleinactive, defaultsecuritylevel,DefaultPayBasis,DefaultPayRate, synchver, ROWGUID) VALUES (?, ?, ?, ?,'2',0,CDate(?),?)",
        "MenuCategories": "INSERT INTO MenuCategories (menucategoryid, menucategorytext, menucategoryinactive, synchver, ROWGUID) VALUES (?, ?, ?, CDate(?),?)",
        "MenuGroups": "INSERT INTO MenuGroups (menugroupid, menugrouptext, menugroupinactive, displayindex,buttoncolor, synchver,ROWGUID) VALUES (?, ?, ?, ?,11198973,CDate(?), ?)",
        "EmployeeFiles": """INSERT INTO EmployeeFiles (employeeid, firstname, lastname, jobtitleid, securitylevel, accesscode, employeeinactive, synchver, TIPSRECEIVED,PAYBASIS,PAYRATE,
                        PREFUSERINTERFACELOCALE,ORDERENTRYUSESECLANG,EMPLOYEEISDRIVER,USESTAFFBANK,SCHEDULENOTENFORCED,USEHOSTESS,ISASERVER,NOCASHIEROUT,
                        DINEINNOTAVAIL,BARNOTAVAIL,TAKEOUTNOTAVAIL,DRIVETHRUNOTAVAIL,DELIVERYNOTAVAIL,USEEMAIL,ROWGUID)
                        VALUES (?, ?, ?, ?, ?, ?, ?, CDate(?),0,2,0,3,0,0,0,0,0,0,0,0,0,0,0,0,0,?)""",
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

        # 🔄 **Insertar datos en Access en el mismo orden de MySQL**
        for table in ["JobTitles","MenuGroups", "EmployeeFiles"]:
            # "MenuCategories",
            print(f"🔄 Procesando {table}...")

            # 🔹 Obtener datos de MySQL ordenados por id
            mysql_cursor.execute(queries[table])
            mysql_data = mysql_cursor.fetchall()

            # 🔹 Obtener los IDs existentes en Access
            # 🔹 Obtener el nombre de la primera columna de la tabla en Access
            access_cursor.execute(f"SELECT TOP 1 * FROM {table}")
            first_column_name = access_cursor.description[0][0]  # Nombre de la primera columna

            # 🔹 Obtener los IDs existentes en Access usando la primera columna detectada
            access_cursor.execute(f"SELECT {first_column_name} FROM {table}")
            existing_ids = {row[0] for row in access_cursor.fetchall()}  # Conjunto de IDs en Access

            try:
                access_conn.autocommit = False  # **Iniciar transacción por tabla**

                for row in mysql_data:
                    primary_key = row[0]  # Primera columna es el ID

                    # 🔹 Verificar si el ID ya existe en Access
                    if primary_key in existing_ids:
                        continue  # Saltar si ya existe

                    updated_at = row[-1]  # Última columna debe ser updated_at en MySQL
                    new_data = list(row)

                    # 🔹 Convertir booleanos si es necesario
                    for i in range(len(new_data)):
                        if isinstance(new_data[i], bool) or (isinstance(new_data[i], int) and new_data[i] in (0, 1)):
                            new_data[i] = convert_boolean(new_data[i])

                    # # 🔹 Convertir `updated_at` a formato Access (MM/DD/YYYY HH:MM:SS AM/PM)
                    # if isinstance(updated_at, datetime):
                    #     new_data[-1] = updated_at.strftime('%m/%d/%Y %I:%M:%S %p')


                    # 🔹 Insertar en Access
                    insert_query = inserts[table]
                    print(f"🔍 DATOS: {new_data}")
                    # print(f"🔍 TOTAL DE PARÁMETROS ESPERADOS: {insert_query.count('?')}")
                    # print(f"🔍 TOTAL DE PARÁMETROS ENVIADOS: {len(new_data)}")
                    access_cursor.execute(insert_query, tuple(new_data))
                    # print(f"✅ Insertado {table} -> ID: {primary_key}")


                # 🔹 Confirmar cambios
                access_conn.commit()
                print(f"✅ Todos los registros de {table} insertados correctamente.")

            except Exception as e:
                access_conn.rollback()  # **Rollback en caso de error**
                print(f"❌ Error en {table}: {e}")
                print("↩️ Se ha realizado rollback en esta tabla.")

        print("✅ Sincronización finalizada.")

    except pyodbc.Error as e:
        print(f"❌ Error general: {e}")

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
    return "Proceso finalizado."
