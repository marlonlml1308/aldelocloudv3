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
        "MenuItems": """SELECT mi.MenuItemText, mi.MenuCategoryID, mi.MenuGroupID, mi.DisplayIndex, mi.DefaultUnitPrice, mi.MenuItemInActive,
            mi.MenuItemInStock, mi.MenuItemTaxable, mi.MenuItemDiscountable, mi.MenuItemType,
            mip.Barcode AS MenuItemPopUpHeaderBarcode,
            mi.GSTApplied, mi.Bar, mi.Barcode, mi.GasPump, mi.LiquorTaxApplied,
            mi.DineInPrice,mi.TakeOutPrice, mi.DriveThruPrice, mi.DeliveryPrice, mi.OrderByWeight
            FROM MenuItems mi
            LEFT JOIN MenuItems mip ON mi.MenuItemPopUpHeaderID = mip.MenuItemID
            WHERE mi.Barcode IS NOT NULL
            ORDER BY mi.MenuItemID""",
    }

    # **4️⃣ Diccionario de INSERTS**
    inserts = {
         "MenuItems": """INSERT INTO products (
        MenuItemText, MenuCategoryID, MenuGroupID, DisplayIndex, DefaultUnitPrice, MenuItemInActive, MenuItemInStock,
        MenuItemTaxable, MenuItemDiscountable, MenuItemType, MenuItemPopUpHeaderID, GSTApplied, Bar, Barcode, GasPump,
        LiquorTaxApplied, DineInPrice, TakeOutPrice, DriveThruPrice, DeliveryPrice, OrderByWeight,created_at,updated_at)
        VALUES
        (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,?, NOW(),NOW());""",
    }

    # **5️⃣ Definir columnas booleanas por tabla**
    boolean_columns = {
        "MenuItems": [5, 6, 7, 8, 11, 12, 15, 19]
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
        try:
            tables = {
                 "Menuitems": {"mysql_table": "products", "mysql_key": "barcode", "access_table": "MenuItems", "access_key": "barcode"},
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
                        QUERY= (f"UPDATE {access_table} SET synchver = #{updated_at_formatted}# WHERE {access_key} = '{record_id}")
                        print(QUERY)
                        access_cursor.execute(f"UPDATE {access_table} SET synchver = #{updated_at_formatted}# WHERE {access_key} = '{record_id}'")
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
