import pyodbc
from datetime import datetime
import decimal
from tkinter import messagebox
import winreg

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
                        DineInPrice=?,TakeOutPrice=?, DriveThruPrice=?, DeliveryPrice=?, OrderByWeight=?,MenuItemPopUpChoiceText=?,MenuItemDescription=?, buttoncolor=?,synchver=CDate(?)
                        WHERE barcode=?""",
    }

    # 📌 Diccionario de queries de inserción para Access
    inserts = {
        "MenuItems": """INSERT INTO MenuItems
        (MenuItemText, MenuCategoryID, MenuGroupID, DisplayIndex, DefaultUnitPrice, MenuItemInActive, MenuItemInStock, MenuItemTaxable, MenuItemDiscountable,
        MenuItemType, MenuItemPopUpHeaderID, GSTApplied, Bar, Barcode, GasPump, LiquorTaxApplied, DineInPrice,TakeOutPrice, DriveThruPrice, DeliveryPrice,
        OrderByWeight,MenuItemPopUpChoiceText,MenuItemDescription,ROWGUID,MenuItemNotification, buttoncolor,showcaption, synchver)
        VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?, CDate(?))""",
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

                # --- NUEVA PARTE: Obtener datos de la tabla items para buscar el popup_header_barcode ---
        try:
            access_cursor.execute("SELECT MenuItemID, Barcode FROM Menuitems")
            items_rows = access_cursor.fetchall()
            # Se asume que el índice 0 es MenuItemID y el 1 es Barcode
            items_data = {str(row[1]).strip(): row[0] for row in items_rows}
        except Exception as ex:
            print(f"❌ Error al obtener datos de la tabla items: {ex}")
            items_data = {}

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
        # Listas separadas
        priority_rows = []
        other_rows = []

        # Separar filas
        for row in mysql_rows:
            if len(row) > 10 and row[10] == 2:  # Asegurar que la columna 10 existe
                print('name: ',row[1],' row10: ',row[10])
                priority_rows.append(row)
                print('priority ',priority_rows)
            else:
                other_rows.append(row)
                # print('other ',other_rows)


        for row in priority_rows:
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
                    # Asegurarse de que popup_header_menuitemid tenga un valor predeterminado
                    # Armar los parámetros para el INSERT (orden basado en el SELECT)
                    # messagebox.showinfo("rows",f"📏 Número de columnas: {len(row)} - Datos: {row}")
                    popup_header_barcode = row[11]
                    # if popup_header_barcode is not None else ""
                    # popup_header_barcode= str(popup_header_barcode)
                    # messagebox.showinfo("popup",f"🔍 Popup Header Barcode: {popup_header_barcode}")
                    # if row[11] is not None else ""
                    # print(f"🔍 Popup Header Barcode: {popup_header_barcode}")
                    # messagebox.showinfo("Popup Header Barcode", f"Popup Header Barcode: {popup_header_barcode}")
                    if popup_header_barcode:
                    # Ejecutar la consulta en Access para obtener el MENUITEMID
                        query_popup = f"SELECT MENUITEMID FROM MENUITEMS WHERE BARCODE = '{popup_header_barcode}'"
                        # messagebox.showinfo("query",f"🔍 Query: {query_popup}")
                        access_cursor.execute(query_popup)
                        result = access_cursor.fetchone()
                        # messagebox.showinfo("result",f"🔍 Result: {result}")

                        if result:
                            popup_header_menuitemid = str(result[0])
                            menuitempopupchoicetext = row[1]
                            # print(f"✅ Encontrado MenuItemID {popup_header_menuitemid} para barcode {popup_header_barcode}")
                        else:
                            popup_header_menuitemid = None
                            menuitempopupchoicetext = None
                            # print(f"⚠️ No se encontró el barcode {popup_header_barcode} en MENUITEMS; se asignará None a MenuItemPopUpHeaderID.")
                    else:
                        # print("⚠️ El popup_header_barcode está vacío.")
                        continue
                    showcaption = True
                    buttoncolor = 16777215
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
                        str(row[14]),   # Barcode
                        row[15],   # GasPump
                        convert_boolean(row[16]),   # LiquorTaxApplied
                        convert_decimal(row[17]),   # DineInPrice
                        convert_decimal(row[18]),   # TakeOutPrice
                        convert_decimal(row[19]),   # DriveThruPrice
                        convert_decimal(row[20]),   # DeliveryPrice
                        convert_boolean(row[21]),   # OrderByWeight
                        menuitempopupchoicetext, #MenuItemPopUpChoiceText
                        row[1], #MenuItemDescription
                        row[14],    # ROWGUID
                        menuitemnotification,    # MenuItemNotification
                        buttoncolor,    # buttoncolor
                        showcaption,    # showcaption
                        synchver_value  # synchver (sin formatear)
                    )
                    insert_query = inserts[table]
                    # (Opcional para depuración) Mostrar query con parámetros
                    insert_query_debug = insert_query
                    for value in insert_params:
                        insert_query_debug = insert_query_debug.replace("?", f"'{value}'", 1)
                    # print(f"🔍 INSERT QUERY FINAL para {mysql_barcode}: {insert_query_debug}")
                    update_params = replace_none_with_null(insert_params)
                    print(f"🔍 DATOS:", row[1])
                    access_cursor.execute(insert_query, insert_params)
                    print(f"🔄 Insertado MenuItems para barcode: {mysql_barcode}")
                except Exception as ex:
                    print(f"❌ Error al insertar para barcode {mysql_barcode}: {ex}")
                    messagebox.showerror("Error",f"❌ Error al insertar para barcode {mysql_barcode}: {ex}")
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

            # Asegurar que updated_at y access_synchver_dt son datetime
            if updated_at and access_synchver_dt:
                if not isinstance(updated_at, datetime):
                    try:
                        updated_at = datetime.strptime(updated_at, "%Y-%m-%d %H:%M:%S")
                    except ValueError:
                        print(f"⚠️ Error al convertir updated_at ({updated_at}) a datetime")
                        updated_at = None

                if not isinstance(access_synchver_dt, datetime):
                    try:
                        access_synchver_dt = datetime.strptime(access_synchver_dt, "%Y-%m-%d %H:%M:%S")
                    except ValueError:
                        print(f"⚠️ Error al convertir access_synchver_dt ({access_synchver_dt}) a datetime")
                        access_synchver_dt = None

            # Actualizar solo si SynchVer no existe o si updated_at es mayor que SynchVer
            if isinstance(updated_at, datetime) and isinstance(access_synchver_dt, datetime) and updated_at > access_synchver_dt:
                # print(f"🔹 No se actualiza {mysql_barcode}: updated_at ({updated_at}) <= SynchVer ({access_synchver_dt})")
                try:
                    updated_at = datetime.strftime(updated_at,"%Y-%m-%d %I:%M:%S")
                    # print(updated_at)
                    # Asegurarse de que popup_header_menuitemid tenga un valor predeterminado
                    popup_header_menuitemid = None
                    menuitempopupchoicetext = None
                    popup_header_barcode = str(row[11]).strip() if row[11] is not None else ""
                    if popup_header_barcode:
                    # Ejecutar la consulta en Access para obtener el MENUITEMID
                        query_popup = f"SELECT MENUITEMID FROM MENUITEMS WHERE BARCODE = '{popup_header_barcode}'"
                        access_cursor.execute(query_popup)
                        result = access_cursor.fetchone()

                        if result:
                            popup_header_menuitemid = str(result[0])
                            menuitempopupchoicetext = row[1]
                            # print(f"✅ Encontrado MenuItemID {popup_header_menuitemid} para barcode {popup_header_barcode}")
                        else:
                            popup_header_menuitemid = None
                            menuitempopupchoicetext = None
                            # print(f"⚠️ No se encontró el barcode {popup_header_barcode} en MENUITEMS; se asignará None a MenuItemPopUpHeaderID.")
                    else:
                        # print("⚠️ El popup_header_barcode está vacío.")
                        continue
                    buttoncolor = 16777215
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
                        str(row[14]),   # Barcode
                        row[15],   # GasPump
                        convert_boolean(row[16]),   # LiquorTaxApplied
                        convert_decimal(row[17]),   # DineInPrice
                        convert_decimal(row[18]),   # TakeOutPrice
                        convert_decimal(row[19]),   # DriveThruPrice
                        convert_decimal(row[20]),   # DeliveryPrice
                        convert_boolean(row[21]),   # OrderByWeight
                        menuitempopupchoicetext, #MenuItemPopUpChoiceText
                        row[1], #MenuItemDescription
                        buttoncolor,    # buttoncolor
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

                #empieza try
                try:
                    print(f"🔍 DATOS: ", row[1])
                    # print(f"🔍 UPDATE QUERY FINAL para {mysql_barcode}: {update_query_debug}")
                    access_cursor.execute(update_query, update_params)
                    # print(f"🔄 Actualizado MenuItems para barcode: {mysql_barcode}")
                except Exception as ex:
                    print(f"❌ Error al ejecutar UPDATE para barcode {mysql_barcode}: {ex}")
                    messagebox.showerror("Error",f"❌ Error al ejecutar UPDATE para barcode {mysql_barcode}: {ex}")
                    print(f"Query: {update_query_debug}, Params: {update_params}")
        ####
        for row in other_rows:
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
                    # Asegurarse de que popup_header_menuitemid tenga un valor predeterminado
                    # Armar los parámetros para el INSERT (orden basado en el SELECT)
                    # messagebox.showinfo("rows",f"📏 Número de columnas: {len(row)} - Datos: {row}")
                    popup_header_barcode = row[11]
                    # if popup_header_barcode is not None else ""
                    # popup_header_barcode= str(popup_header_barcode)
                    # messagebox.showinfo("popup",f"🔍 Popup Header Barcode: {popup_header_barcode}")
                    # if row[11] is not None else ""
                    # print(f"🔍 Popup Header Barcode: {popup_header_barcode}")
                    # messagebox.showinfo("Popup Header Barcode", f"Popup Header Barcode: {popup_header_barcode}")
                    if popup_header_barcode:
                    # Ejecutar la consulta en Access para obtener el MENUITEMID
                        query_popup = f"SELECT MENUITEMID FROM MENUITEMS WHERE BARCODE = '{popup_header_barcode}'"
                        # messagebox.showinfo("query",f"🔍 Query: {query_popup}")
                        access_cursor.execute(query_popup)
                        result = access_cursor.fetchone()
                        # messagebox.showinfo("result",f"🔍 Result: {result}")

                        if result:
                            popup_header_menuitemid = str(result[0])
                            menuitempopupchoicetext = row[1]
                            print(f"✅ Encontrado MenuItemID {popup_header_menuitemid} para barcode {popup_header_barcode}")
                        else:
                            popup_header_menuitemid = None
                            menuitempopupchoicetext = None
                            print(f"⚠️ No se encontró el barcode {popup_header_barcode} en MENUITEMS; se asignará None a MenuItemPopUpHeaderID.")
                    else:
                        print("⚠️ El popup_header_barcode está vacío.")
                    showcaption = True
                    buttoncolor = 16777215
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
                        str(row[14]),   # Barcode
                        row[15],   # GasPump
                        convert_boolean(row[16]),   # LiquorTaxApplied
                        convert_decimal(row[17]),   # DineInPrice
                        convert_decimal(row[18]),   # TakeOutPrice
                        convert_decimal(row[19]),   # DriveThruPrice
                        convert_decimal(row[20]),   # DeliveryPrice
                        convert_boolean(row[21]),   # OrderByWeight
                        menuitempopupchoicetext, #MenuItemPopUpChoiceText
                        row[1], #MenuItemDescription
                        row[14],    # ROWGUID
                        menuitemnotification,    # MenuItemNotification
                        buttoncolor,    # buttoncolor
                        showcaption,    # showcaption
                        synchver_value  # synchver (sin formatear)
                    )
                    insert_query = inserts[table]
                    # (Opcional para depuración) Mostrar query con parámetros
                    insert_query_debug = insert_query
                    for value in insert_params:
                        insert_query_debug = insert_query_debug.replace("?", f"'{value}'", 1)
                    # print(f"🔍 INSERT QUERY FINAL para {mysql_barcode}: {insert_query_debug}")
                    update_params = replace_none_with_null(insert_params)
                    print(f"🔍 DATOS: ", row[1])
                    access_cursor.execute(insert_query, insert_params)
                    print(f"🔄 Insertado MenuItems para barcode: {mysql_barcode}")
                except Exception as ex:
                    print(f"❌ Error al insertar para barcode {mysql_barcode}: {ex}")
                    messagebox.showerror("Error",f"❌ Error al insertar para barcode {mysql_barcode}: {ex}")
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

            # Asegurar que updated_at y access_synchver_dt son datetime
            if updated_at and access_synchver_dt:
                if not isinstance(updated_at, datetime):
                    try:
                        updated_at = datetime.strptime(updated_at, "%Y-%m-%d %H:%M:%S")
                    except ValueError:
                        print(f"⚠️ Error al convertir updated_at ({updated_at}) a datetime")
                        updated_at = None

                if not isinstance(access_synchver_dt, datetime):
                    try:
                        access_synchver_dt = datetime.strptime(access_synchver_dt, "%Y-%m-%d %H:%M:%S")
                    except ValueError:
                        print(f"⚠️ Error al convertir access_synchver_dt ({access_synchver_dt}) a datetime")
                        access_synchver_dt = None

            # Actualizar solo si SynchVer no existe o si updated_at es mayor que SynchVer
            if isinstance(updated_at, datetime) and isinstance(access_synchver_dt, datetime) and updated_at > access_synchver_dt:
                # print(f"🔹 No se actualiza {mysql_barcode}: updated_at ({updated_at}) <= SynchVer ({access_synchver_dt})")
                try:
                    updated_at = datetime.strftime(updated_at,"%Y-%m-%d %I:%M:%S")
                    # print(updated_at)
                    # Asegurarse de que popup_header_menuitemid tenga un valor predeterminado
                    popup_header_menuitemid = None
                    menuitempopupchoicetext = None
                    popup_header_barcode = str(row[11]).strip() if row[11] is not None else ""
                    if popup_header_barcode:
                    # Ejecutar la consulta en Access para obtener el MENUITEMID
                        query_popup = f"SELECT MENUITEMID FROM MENUITEMS WHERE BARCODE = '{popup_header_barcode}'"
                        access_cursor.execute(query_popup)
                        result = access_cursor.fetchone()

                        if result:
                            popup_header_menuitemid = str(result[0])
                            menuitempopupchoicetext = row[1]
                            # print(f"✅ Encontrado MenuItemID {popup_header_menuitemid} para barcode {popup_header_barcode}")
                        else:
                            popup_header_menuitemid = None
                            menuitempopupchoicetext = None
                            # print(f"⚠️ No se encontró el barcode {popup_header_barcode} en MENUITEMS; se asignará None a MenuItemPopUpHeaderID.")
                    else:
                        # print("⚠️ El popup_header_barcode está vacío.")
                        continue
                    buttoncolor = 16777215
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
                        str(row[14]),   # Barcode
                        row[15],   # GasPump
                        convert_boolean(row[16]),   # LiquorTaxApplied
                        convert_decimal(row[17]),   # DineInPrice
                        convert_decimal(row[18]),   # TakeOutPrice
                        convert_decimal(row[19]),   # DriveThruPrice
                        convert_decimal(row[20]),   # DeliveryPrice
                        convert_boolean(row[21]),   # OrderByWeight
                        menuitempopupchoicetext, #MenuItemPopUpChoiceText
                        row[1], #MenuItemDescription
                        buttoncolor,    # buttoncolor
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

                #empieza try
                try:
                    print(f"🔍 DATOS: ", row[1])
                    # print(f"🔍 UPDATE QUERY FINAL para {mysql_barcode}: {update_query_debug}")
                    access_cursor.execute(update_query, update_params)
                    # print(f"🔄 Actualizado MenuItems para barcode: {mysql_barcode}")
                except Exception as ex:
                    print(f"❌ Error al ejecutar UPDATE para barcode {mysql_barcode}: {ex}")
                    messagebox.showerror("Error",f"❌ Error al ejecutar UPDATE para barcode {mysql_barcode}: {ex}")
                    print(f"Query: {update_query_debug}, Params: {update_params}")
####
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
def updatep():
    access_conn, access_cursor, mysql_conn, mysql_cursor = dbconn()
    updateproducts(access_conn, access_cursor, mysql_conn, mysql_cursor)

updatep()
print("============================================")
