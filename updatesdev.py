import pyodbc
import mysql.connector
from datetime import datetime

# 🔹 Conexión a Access
access_conn = pyodbc.connect(    "DRIVER={Microsoft Access Driver (*.mdb, *.accdb)};"
    "DBQ=D:\\INFORMECIERRE\\PCHIA\\PASTAIO.mdb;"
    "PWD=;")
access_cursor = access_conn.cursor()

# 🔹 Conexión a MySQL
mysql_conn = mysql.connector.connect(host="localhost", user="root", password="", database="laravel")
mysql_cursor = mysql_conn.cursor()

# 🔹 Diccionario de consultas
queries = {
    "MenuGroups": "SELECT id, menugrouptext, menugroupinactive, displayindex, updated_at FROM Groups"
}

updates = {
    "MenuGroups": "UPDATE MenuGroups SET menugrouptext=?, menugroupinactive=?, displayindex=?, synchver=? WHERE menugroupid=?"
}

# 🔄 Sincronización de datos
for table in ["MenuGroups"]:
    print(f"🔄 Sincronizando {table}...")

    # 🔹 Obtener nombres de columnas en Access
    access_cursor.execute(f"SELECT top 1 * FROM {table}")
    column_names = [desc[0] for desc in access_cursor.description]  # Lista con los nombres de columnas

    # 🔹 Obtener datos de Access
    print(f"SELECT * FROM {table}")
    access_cursor.execute(f"SELECT * FROM {table}")
    access_data = {row[0]: row for row in access_cursor.fetchall()}  # Diccionario con la PK como clave

    # 🔹 Obtener datos de MySQL
    mysql_cursor.execute(queries[table])
    mysql_data = mysql_cursor.fetchall()

    # 🔹 Procesar datos
    for row in mysql_data:
        primary_key = row[0]  # Primera columna como clave primaria
        updated_at = row[-1]  # Última columna (updated_at en MySQL)

        # 🔹 Convertir `updated_at` a formato Access (MM/DD/YYYY HH:MM:SS AM/PM)
        if isinstance(updated_at, datetime):
            updated_at_access = f"#{updated_at.strftime('%m/%d/%Y %I:%M:%S %p')}#"
        else:
            updated_at_access = None

        # 🔹 Obtener `synchver` de Access
        if primary_key in access_data:
            access_row = access_data[primary_key]
            if "SynchVer" in column_names:
                    synchver_index = column_names.index("SynchVer")
                    synchver = access_row[synchver_index]  # Obtener synchver en la posición correcta

                    try:
                        if isinstance(synchver, str):
                            synchver = datetime.strptime(synchver, "%m/%d/%Y %I:%M:%S %p")

                        # 🔹 Comparar fechas y actualizar si es necesario
                        if isinstance(updated_at, datetime) and isinstance(synchver, datetime) and updated_at > synchver:
                            update_query = updates[table]
                            new_data = list(row)[1:]
                            # 🔹 Agregar el `updated_at` convertido y `primary_key`
                            # new_data.append(updated_at_access)
                            # new_data.append(primary_key)
                            # ✅ Verificar que `updated_at_access` existe
                            updated_at_access = updated_at.strftime("%m/%d/%Y %I:%M:%S %p")  # Formato de Access
                            primary_key = int(primary_key)  # Asegura que sea un entero
                            new_data_with_id = new_data + [updated_at_access] + [primary_key]

                            #new_data_with_id = new_data + [primary_key]
                            print('new',new_data_with_id)
                            # 🔍 Construir y mostrar la consulta con valores interpolados
                            query_with_values = update_query
                            temp_data = new_data_with_id[:]
                            for value in new_data_with_id:
                                if isinstance(value, str):
                                    query_with_values = query_with_values.replace("?", f"'{value}'", 1)
                                elif isinstance(value, datetime):
                                    query_with_values = query_with_values.replace("?", value.strftime("#%m/%d/%Y %I:%M:%S %p#"), 1)
                                    print('1',query_with_values)
                                else:
                                    query_with_values = query_with_values.replace("?", str(value), 1)

                            print(f"🔍 QUERY EJECUTADA: {query_with_values}")

                            # 🔹 Ejecutar actualización en Access
                            access_cursor.execute(update_query, new_data_with_id)
                            access_conn.commit()

                            print(f"✅ Actualizado {table}: {primary_key}")
                    except ValueError:
                        print(f"⚠ Error al convertir synchver: {synchver}")
        else:
            print(f"✅ No hay cambios para {table}")

# 🔹 Cerrar conexiones
mysql_cursor.close()
mysql_conn.close()
access_cursor.close()
access_conn.close()
print("✅ Conexiones cerradas.")
