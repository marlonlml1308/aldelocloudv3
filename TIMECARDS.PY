import pyodbc
from datetime import datetime

# 📌 Configuración de la conexión a Access
access_conn_str = (
    "DRIVER={Microsoft Access Driver (*.mdb, *.accdb)};"
    "DBQ=D:\\INFORMECIERRE\\p125\\PASTAIO.mdb;"
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
        "EmployeeTimecards": """SELECT employeeid, Format(workdate, 'yyyy-mm-dd') AS workdate1,Format(clockintime, 'yyyy-mm-dd hh:nn:ss') AS clockintime1,
      Format(clockouttime, 'yyyy-mm-dd hh:nn:ss') AS clockouttime1, Format(break1begintime, 'yyyy-mm-dd hh:nn:ss') AS break1begintime1,
      Format(break1endtime, 'yyyy-mm-dd hh:nn:ss') AS break1endtime1,TotalWorkMinutes, 2 AS branch
      FROM EmployeeTimeCards WHERE SynchVer IS NULL AND clockouttime IS NOT NULL and WORKDATE >= #01/01/2025#""",
    }

    # **4️⃣ Diccionario de INSERTS**
    inserts = {
        "EmployeeTimecards": "INSERT INTO Timecards (employeeid, workdate, clockintime,clockouttime,break1begintime,break1endtime,totalworkminutes,branchid,created_at,updated_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, NOW(),NOW())",
    }

    # **5️⃣ Definir columnas booleanas por tabla**
    boolean_columns = {
        # "JobTitles": [1],  # Tercera columna (jobtitleinactive) es booleana
    }

    querynull="UPDATE EMPLOYEETIMECARDS SET SYNCHVER=NULL"
    access_cursor.execute(querynull)
    access_cursor.commit()
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
                for data in converted_rows:
                    try:
                        # 🔹 Formatear la consulta con los valores
                        query_str = inserts[table].replace("?", "'{}'").format(*data)
                        print(f"📝 Query generado para {table}: {query_str}")  # 📌 LOG del query
                        mysql_cursor.execute(inserts[table], data)
                        access_cursor.execute(f"UPDATE EMPLOYEETIMECARDS SET synchver = NOW() WHERE SYNCHVER IS NULL")
                        access_conn.commit()
                    except Exception as e:
                        print(f"❌ Error ejecutando query en {table}: {e}")
                        print(f"🔍 Query con error: {query_str}")
            # 🔹 Confirmar transacción en Access
            mysql_cursor.commit()
        except Exception as e:
            # 🔴 Rollback SOLO en la tabla actual
            access_conn.rollback()
            print(f"❌ Error en {table}: {e}")

    mysql_conn.commit()
except pyodbc.Error as e:
    print(f"❌ Error: {e}")
    mysql_conn.rollback()
    access_conn.rollback()
finally:
    # Cerrar conexiones
    access_cursor.close()
    access_conn.close()
    mysql_cursor.close()
    mysql_conn.close()
    print("✅ Conexiones cerradas.")
print("✅ Migración completada exitosamente.")
