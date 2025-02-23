import pyodbc
from datetime import datetime
import decimal
from tkinter import messagebox

# # 📌 Configuración de la conexión a Access
# access_conn_str = (
#     "DRIVER={Microsoft Access Driver (*.mdb, *.accdb)};"
#     "DBQ=D:\\INFORMECIERRE\\PCHIA\\PASTAIO.mdb;"
#     "PWD=;"
# )

# # 📌 Configuración de la conexión a MySQL
# mysql_conn_str = (
#     "DRIVER={MySQL ODBC 9.2 ANSI Driver};"
#     "SERVER=127.0.0.1;PORT=3306;"
#     "DATABASE=laravel;"
#     "USER=root;PASSWORD=;"
#     "OPTION=3;"
# )
def updateproducts(access_conn, access_cursor, mysql_conn, mysql_cursor):# 📌 Diccionario de queries para obtener datos de MySQL
    queries = {
        "MenuItems": """SELECT Barcode, MenuItemText, MenuCategoryID, MenuGroupID, DisplayIndex, DefaultUnitPrice,
                        MenuItemInActive, MenuItemInStock, MenuItemTaxable, MenuItemDiscountable, MenuItemType,
                        MenuItemPopUpHeaderID, GSTApplied, Bar, Barcode, GasPump, LiquorTaxApplied,
                        DineInPrice,TakeOutPrice, DriveThruPrice, DeliveryPrice, OrderByWeight, updated_at
                        FROM products""",
    }

    # 📌 Diccionario de queries de actualización para Access
    updates = {
        "MenuItems": """UPDATE MenuItems SET MenuItemText=?, MenuCategoryID=?, MenuGroupID=?, DisplayIndex=?,
                        DefaultUnitPrice=?, MenuItemInActive=?, MenuItemInStock=?, MenuItemTaxable=?, MenuItemDiscountable=?,
                        MenuItemType=?, MenuItemPopUpHeaderID=?, GSTApplied=?, Bar=?, Barcode=?, GasPump=?, LiquorTaxApplied=?,
                        DineInPrice=?,TakeOutPrice=?, DriveThruPrice=?, DeliveryPrice=?, OrderByWeight=?,MenuItemPopUpChoiceText=?,MenuItemDescription=?, synchver=CDate(?)
                        WHERE barcode=?""",
    }

    # 📌 Diccionario de queries de inserción para Access
    inserts = {
        "MenuItems": """INSERT INTO MenuItems
        (MenuItemText, MenuCategoryID, MenuGroupID, DisplayIndex, DefaultUnitPrice, MenuItemInActive, MenuItemInStock, MenuItemTaxable, MenuItemDiscountable,
        MenuItemType, MenuItemPopUpHeaderID, GSTApplied, Bar, Barcode, GasPump, LiquorTaxApplied, DineInPrice,TakeOutPrice, DriveThruPrice, DeliveryPrice,
        OrderByWeight,MenuItemPopUpChoiceText,MenuItemDescription,ROWGUID,MenuItemNotification, synchver)
        VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?, CDate(?))""",
    }

    # 📌 Mapeo de nombres de tablas entre MySQL y Access
    tables = {
        "MenuItems": {"mysql_table": "products", "mysql_key": "Barcode", "access_table": "MenuItems", "access_key": "Barcode"},
    }

    # **Definir columnas booleanas por tabla** (índices basados en el SELECT)
    boolean_columns = {
        "MenuItems": [5, 6, 7, 8, 11, 12, 15, 19],
    }

    # 📌 Función para convertir booleanos a formato Access
    def convert_boolean(value):
        return True if value == 1 else False
    def convert_decimal(value):
        return float(value) if isinstance(value, decimal.Decimal) else value
    def replace_none_with_null(values):
        return tuple("NULL" if value is None else value for value in values)

    try:
        # Conectar a Access y MySQL
        # access_conn = pyodbc.connect(access_conn_str)
        # mysql_conn = pyodbc.connect(mysql_conn_str)

        # access_cursor = access_conn.cursor()
        # mysql_cursor = mysql_conn.cursor()

        table = "MenuItems"
        mysql_table = tables[table]["mysql_table"]      # "products"
        access_table = tables[table]["access_table"]      # "MenuItems"
        mysql_key = tables[table]["mysql_key"]            # "Barcode"
        access_key = tables[table]["access_key"]          # "Barcode"

        # --- Obtener datos de Access ---
        # Obtener lista de columnas de Access
        access_cursor.execute(f"SELECT TOP 1 * FROM {access_table}")
        access_columns = [desc[0] for desc in access_cursor.description]
        if access_key not in access_columns:
            raise ValueError(f"La columna {access_key} no se encontró en Access. Columnas: {access_columns}")
        access_key_index = access_columns.index(access_key)

        # Verificar si existe el campo SynchVer en Access
        if "SynchVer" in access_columns:
            synchver_index = access_columns.index("SynchVer")
        else:
            synchver_index = None

        # Construir diccionario con claves = valor real de Barcode (normalizado)
        access_cursor.execute(f"SELECT * FROM {access_table}")
        access_rows = access_cursor.fetchall()
        access_data = {str(row[access_key_index]).strip(): row for row in access_rows}
        # Verificar que la columna MenuItemID exista y obtener su índice
        if "MenuItemID" in access_columns:
            menuitemid_index = access_columns.index("MenuItemID")
        else:
            raise ValueError("La columna MenuItemID no se encontró en Access.")
        # print(f"🔎 Claves (Barcode) en Access: {list(access_data.keys())}")

        # --- Obtener datos de MySQL ---
        query_mysql = queries[table]
        mysql_cursor.execute(query_mysql)
        mysql_rows = mysql_cursor.fetchall()
        mysql_columns = [desc[0] for desc in mysql_cursor.description]
        if mysql_key not in mysql_columns:
            raise ValueError(f"La columna {mysql_key} no se encontró en MySQL. Columnas: {mysql_columns}")
        mysql_key_index = mysql_columns.index(mysql_key)

        # Iniciar transacción en Access
        access_conn.autocommit = False

        # --- Comparar y actualizar/inserción ---
        # --- Dentro del bucle que recorre cada registro de MySQL ---
        for row in mysql_rows:
            # Obtener barcode de MySQL (normalizado)
            mysql_barcode = str(row[mysql_key_index]).strip()
            # Obtener updated_at (última columna, se espera que sea datetime)
            updated_at = row[-1]
            if not isinstance(updated_at, datetime):
                print(f"❌ updated_at no es datetime para barcode {mysql_barcode}.")
                continue

            # Usar el valor de updated_at sin formatear
            synchver_value = updated_at
            menuitemnotification = "1"

            if mysql_barcode not in access_data:
                # Si el barcode no existe, se inserta el producto.
                print(f"❌ Barcode {mysql_barcode} no encontrado en Access. Se creará el producto.")
                try:
                    # Armar los parámetros para el INSERT (orden basado en el SELECT)
                    popup_header_barcode = str(row[11]).strip()
                    if popup_header_barcode in access_data:
                        popup_header_menuitemid = access_data[popup_header_barcode][menuitemid_index]
                        # print(f"✅ Encontrado MenuItemID {popup_header_menuitemid} para barcode {popup_header_barcode}")
                    else:
                        popup_header_menuitemid = row[11]
                        print(f"⚠️ No se encontró en Access el barcode {popup_header_barcode} para MenuItemPopUpHeaderID, se usará el valor original.")

                    insert_params = (
                        row[1],    # MenuItemText
                        row[2],    # MenuCategoryID
                        row[3],    # MenuGroupID
                        row[4],    # DisplayIndex
                        convert_decimal(row[5]),    # DefaultUnitPrice
                        convert_boolean(row[6]),
                        convert_boolean(row[7]),
                        convert_boolean(row[8]),
                        convert_boolean(row[9]),
                        row[10],   # MenuItemType
                        popup_header_menuitemid,   # MenuItemPopUpHeaderID
                        convert_boolean(row[12]),   # GSTApplied
                        convert_boolean(row[13]),   # Bar
                        row[14],   # Barcode
                        row[15],   # GasPump
                        convert_boolean(row[16]),   # LiquorTaxApplied
                        convert_decimal(row[17]),   # DineInPrice
                        convert_decimal(row[18]),   # TakeOutPrice
                        convert_decimal(row[19]),   # DriveThruPrice
                        convert_decimal(row[20]),   # DeliveryPrice
                        convert_boolean(row[21]),   # OrderByWeight
                        row[1], #MenuItemPopUpChoiceText
                        row[1], #MenuItemDescription
                        row[14],    # ROWGUID
                        menuitemnotification,    # MenuItemNotification
                        synchver_value  # synchver (sin formatear)
                    )
                    insert_query = inserts[table]
                    # (Opcional para depuración) Mostrar query con parámetros
                    insert_query_debug = insert_query
                    for value in insert_params:
                        insert_query_debug = insert_query_debug.replace("?", f"'{value}'", 1)
                    # print(f"🔍 INSERT QUERY FINAL para {mysql_barcode}: {insert_query_debug}")
                    update_params = replace_none_with_null(insert_params)
                    print(f"🔍 DATOS: {update_params}")
                    access_cursor.execute(insert_query, insert_params)
                    print(f"🔄 Insertado MenuItems para barcode: {mysql_barcode}")
                except Exception as ex:
                    print(f"❌ Error al insertar para barcode {mysql_barcode}: {ex}")
                    messagebox.showerror("Error"f"❌ Error al insertar para barcode {mysql_barcode}: {ex}")
                continue  # Pasa al siguiente registro

            # Si el producto existe, obtener su registro de Access
            access_row = access_data[mysql_barcode]
            # Extraer SynchVer de Access, si existe, y convertirlo a datetime si es necesario
            if synchver_index is not None:
                access_synchver = access_row[synchver_index]
                if isinstance(access_synchver, str):
                    try:
                        access_synchver_dt = datetime.strptime(access_synchver, "%m/%d/%Y %I:%M:%S %p")
                    except Exception as ex:
                        print(f"⚠️ Error al convertir SynchVer '{access_synchver}' para barcode {mysql_barcode}: {ex}")
                        access_synchver_dt = None
                elif isinstance(access_synchver, datetime):
                    access_synchver_dt = access_synchver
                else:
                    access_synchver_dt = None
            else:
                access_synchver_dt = None

            # Actualizar solo si SynchVer no existe o si updated_at es mayor que SynchVer
            if access_synchver_dt is not None and updated_at <= access_synchver_dt:
                # print(f"🔹 No se actualiza {mysql_barcode}: updated_at ({updated_at}) <= SynchVer ({access_synchver_dt})")
                continue

            try:
                updated_at = datetime.strftime(updated_at,"%Y-%m-%d %I:%M:%S")
                print(updated_at)
                popup_header_barcode = str(row[11]).strip()
                if popup_header_barcode in access_data:
                    popup_header_menuitemid = access_data[popup_header_barcode][menuitemid_index]
                    # print(f"✅ Encontrado MenuItemID {popup_header_menuitemid} para barcode {popup_header_barcode}")
                else:
                    popup_header_menuitemid = row[11]
                    print(f"⚠️ No se encontró en Access el barcode {popup_header_barcode} para MenuItemPopUpHeaderID, se usará el valor original.")

                update_params = (
                    row[1],    # MenuItemText
                    row[2],    # MenuCategoryID
                    row[3],    # MenuGroupID
                    row[4],    # DisplayIndex
                    convert_decimal(row[5]),    # DefaultUnitPrice
                    convert_boolean(row[6]),
                    convert_boolean(row[7]),
                    convert_boolean(row[8]),
                    convert_boolean(row[9]),
                    row[10],   # MenuItemType
                    popup_header_menuitemid,   # MenuItemPopUpHeaderID
                    convert_boolean(row[12]),   # GSTApplied
                    convert_boolean(row[13]),   # Bar
                    row[14],   # Barcode
                    row[15],   # GasPump
                    convert_boolean(row[16]),   # LiquorTaxApplied
                    convert_decimal(row[17]),   # DineInPrice
                    convert_decimal(row[18]),   # TakeOutPrice
                    convert_decimal(row[19]),   # DriveThruPrice
                    convert_decimal(row[20]),   # DeliveryPrice
                    convert_boolean(row[21]),   # OrderByWeight
                    row[1], #MenuItemPopUpChoiceText
                    row[1], #MenuItemDescription
                    updated_at,  # synchver (nuevo updated_at sin formatear)
                    mysql_barcode    # WHERE barcode = ?
                )
            except Exception as ex:
                print(f"❌ Error al preparar parámetros para barcode {mysql_barcode}: {ex}")
                continue

            update_query = updates[table]
            update_query_debug = update_query
            for value in update_params:
                update_query_debug = update_query_debug.replace("?", f"'{value}'", 1)
            # update_params = replace_none_with_null(update_params)
            # print(f"🔍 UPDATE QUERY FINAL para {mysql_barcode}: {update_query_debug}")

            try:
                access_cursor.execute(update_query, update_params)
                # print(f"🔄 Actualizado MenuItems para barcode: {mysql_barcode}")
            except Exception as ex:
                print(f"❌ Error al ejecutar UPDATE para barcode {mysql_barcode}: {ex}")
                messagebox.showerror("Error"f"❌ Error al ejecutar UPDATE para barcode {mysql_barcode}: {ex}")
                # print(f"Query: {update_query_debug}, Params: {update_params}")

        # Confirmar transacción
        try:
            access_conn.commit()
            print("✅ Cambios confirmados en MenuItems")
        except Exception as ex:
            access_conn.rollback()
            print(f"❌ Error al confirmar cambios: {ex}")
            messagebox.showerror("Error",f"❌ Error al confirmar cambios: {ex}")
    except Exception as e:
        print(f"❌ Error general: {e}")
        messagebox.showerror("Error", f"❌ Error general: {e}")

    finally:
        if access_cursor:
            access_cursor.close()
        if mysql_cursor:
            mysql_cursor.close()
        if access_conn:
            access_conn.close()
        if mysql_conn:
            mysql_conn.close()
        print("✅ Conexiones cerradas.")
        return "Proceso finalizado."
