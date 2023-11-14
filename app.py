from flask import Flask, request
from flask_restx import Api, Resource, fields
from datetime import datetime
from flask_cors import CORS
from PIL import Image
import pymysql

import logging
import base64
import json
import io

logging.basicConfig(level=logging.ERROR)

from database import MysqlConnection

app = Flask(__name__)
CORS(app)
api = Api(app)

ns = api.namespace("SmartCanteen")
ALLOWED_EXTENSIONS = {"png", "jpg"}


@ns.route("/")
class storeDetail(Resource):
    def get(self):
        try:
            return {"message": "Welcome to the SmartCanteen API!"}, 200

        except Exception as e:
            return {
                "message": "An error occurred while processing the request.",
                "error": str(e),
            }, 500


@ns.route("/store")
class storeData(Resource):
    def get(self):
        try:
            db_connection = MysqlConnection()
            connection = db_connection.connect_mysql()
            cursor = connection.cursor()

            query = (
                "SELECT store_name, store_username, store_type, store_locate FROM store"
            )
            cursor.execute(query)
            store_data = cursor.fetchall()
            cursor.close()
            connection.close()

            store_list = []
            for row in store_data:
                store_dict = {
                    "store_name": row[0],
                    "store_username": row[1],
                    "store_type": row[2],
                    "store_locate": row[3],
                }
                store_list.append(store_dict)

            return store_list, 200
        except Exception as e:
            return {
                "message": "An error occurred while retrieving data.",
                "error": str(e),
            }, 500


@ns.route("/store/register")
class Register(Resource):
    def post(self):
        try:
            required_fields = [
                "storeName",
                "username",
                "number",
                "password",
                "storetype",
                "stayAt",
            ]
            missing_fields = [
                field for field in required_fields if field not in request.form
            ]
            if missing_fields:
                return {"error": f"Missing fields: {', '.join(missing_fields)}"}, 400

            db_connection = MysqlConnection()
            connection = db_connection.connect_mysql()
            cursor = connection.cursor()

            store_name = request.form["storeName"]
            store_username = request.form["username"]
            store_number = request.form["number"]
            store_pwd = request.form["password"]
            store_type = request.form["storetype"]
            stay_at = request.form["stayAt"]

            query = "INSERT INTO store (store_name, store_username, store_number, store_pwd, store_type, store_locate, store_qr_code, store_image) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"

            if "qrcodeImage" in request.files:
                qrcode_image = request.files["qrcodeImage"].read()

                # Check if the image is in PNG format
                if qrcode_image.startswith(b"\x89PNG\r\n\x1a\n"):
                    # Convert PNG to JPEG
                    image = Image.open(io.BytesIO(qrcode_image))
                    buffer = io.BytesIO()
                    image.convert("RGB").save(buffer, format="JPEG")
                    qrcode_image = buffer.getvalue()
            else:
                qrcode_image = None

            if "storeImage" in request.files:
                store_image = request.files["storeImage"].read()

                if store_image.startswith(b"\x89PNG\r\n\x1a\n"):
                    image = Image.open(io.BytesIO(store_image))
                    buffer = io.BytesIO()
                    image.convert("RGB").save(buffer, format="JPEG")
                    store_image = buffer.getvalue()
            else:
                store_image = None

            cursor.execute(
                query,
                (
                    store_name,
                    store_username,
                    store_number,
                    store_pwd,
                    store_type,
                    stay_at,
                    qrcode_image,
                    store_image,
                ),
            )

            connection.commit()

            cursor.close()
            connection.close()

            return {"message": "store registration successful"}, 201

        except Exception as e:
            return {
                "message": "An error occurred while processing the request.",
                "error": str(e),
            }, 500


@ns.route("/store/login")
class Login(Resource):
    def post(self):
        try:
            data = request.get_json()

            if "username" in data and "password" in data:
                username = data.get("username")
                password = data.get("password")

                db_connection = MysqlConnection()
                connection = db_connection.connect_mysql()
                cursor = connection.cursor()

                query = "SELECT store_id FROM store WHERE (store_username = %s OR store_number = %s) AND store_pwd = %s"
                cursor.execute(query, (username, username, password))
                result = cursor.fetchone()

                cursor.close()
                connection.close()

                if result:
                    return {
                        "message": "Login successful",
                        "storid": result[0],
                    }, 200
                else:
                    # Username not found in the database
                    return {"message": "Username not found or incorrect password"}, 404

            return {
                "message": "Invalid request data. 'username' and 'password' are required."
            }, 400

        except Exception as e:
            return {
                "message": "An error occurred while processing the request.",
                "error": str(e),
            }, 500


@ns.route("/store/dashboard")
class storeDashboard(Resource):
    def get(self):
        try:
            id = request.args.get("id")
            if id is None:
                return {"message": "ID parameter is missing in the request"}, 400

            db_connection = MysqlConnection()
            connection = db_connection.connect_mysql()
            cursor = connection.cursor()

            query = "SELECT store_name, store_locate, store_image, open_time, close_time FROM store LEFT JOIN openTime ON store.store_id = openTime.store_id WHERE store.store_id = %s"
            cursor.execute(query, (id,))
            store_data = cursor.fetchone()

            cursor.close()
            connection.close()

            if store_data:
                # image_data = io.BytesIO(store_data[2])
                # image = Image.open(image_data)
                # image.show()
                store_data = list(store_data)
                store_data[2] = base64.b64encode(store_data[2]).decode("utf-8")

                store_detail = {
                    "store_name": store_data[0],
                    "store_locate": store_data[1],
                    "store_image": store_data[2],
                    "open_time": store_data[3],
                    "close_time": store_data[4],
                }
                return {"data": store_detail}, 200
            else:
                return {"message": f"Store with ID {id} not found"}, 404

        except Exception as e:
            return {
                "message": "An error occurred while processing the request.",
                "error": str(e),
            }, 500


@ns.route("/store/menutype")
class Menutype(Resource):
    def post(self):
        try:
            data = request.get_json()

            if "storeid" in data and "menuType" in data:
                storeid = data.get("storeid")
                menuType = data.get("menuType")

                db_connection = MysqlConnection()
                connection = db_connection.connect_mysql()
                cursor = connection.cursor()
                query = (
                    "INSERT INTO menu_type (menu_type_name, store_id) VALUES (%s, %s)"
                )
                cursor.execute(query, (menuType, storeid))
                connection.commit()

                cursor.close()
                connection.close()

                return {
                    "message": "Menu type inserted successfully",
                }, 201

            return {
                "message": "Invalid request data. 'storeid' and 'menuType' are required."
            }, 400

        except Exception as e:
            return {
                "message": "An error occurred while processing the request.",
                "error": str(e),
            }, 500

    def get(self):
        try:
            storeid = request.args.get("storeid")

            if not storeid:
                return {"message": "Missing 'storeid' parameter"}, 400

            db_connection = MysqlConnection()
            connection = db_connection.connect_mysql()
            cursor = connection.cursor()

            query = "SELECT * FROM menu_type WHERE store_id = %s"
            cursor.execute(query, (storeid,))
            menu_types = cursor.fetchall()

            cursor.close()
            connection.close()

            menu_type_list = [
                {"menu_type_id": row[0], "menu_type_name": row[1], "store_id": row[2]}
                for row in menu_types
            ]

            return {"data": menu_type_list}, 200

        except Exception as e:
            return {
                "message": "An error occurred while processing the request.",
                "error": str(e),
            }, 500


@ns.route("/store/menutype/<int:menuTypeid>")
class ManageMenuType(Resource):
    def put(self, menuTypeid):
        try:
            data = request.get_json()

            if "menuType" in data:
                new_menu_type_name = data.get("menuType")

                db_connection = MysqlConnection()
                connection = db_connection.connect_mysql()
                cursor = connection.cursor()

                query = (
                    "UPDATE menu_type SET menu_type_name = %s WHERE menu_type_id = %s"
                )
                cursor.execute(query, (new_menu_type_name, menuTypeid))
                connection.commit()

                cursor.close()
                connection.close()

                return {
                    "message": "Menu type updated successfully",
                }, 200

            return {"message": "Invalid request data. 'menuType' is required."}, 400

        except Exception as e:
            return {
                "message": "An error occurred while processing the request.",
                "error": str(e),
            }, 500

    def delete(self, menuTypeid):
        try:
            db_connection = MysqlConnection()
            connection = db_connection.connect_mysql()
            cursor = connection.cursor()

            query = "SELECT * FROM menu_type WHERE menu_type_id = %s"
            cursor.execute(query, (menuTypeid,))
            existing_menu_type = cursor.fetchone()

            if not existing_menu_type:
                return {"message": "Menu type not found"}, 404

            delete_query = "DELETE FROM menu_type WHERE menu_type_id = %s"
            cursor.execute(delete_query, (menuTypeid,))
            connection.commit()

            cursor.close()
            connection.close()

            return {"message": "Menu type deleted successfully"}, 200

        except Exception as e:
            return {
                "message": "An error occurred while processing the request.",
                "error": str(e),
            }, 500


@ns.route("/store/addon")
class Addon(Resource):
    def get(self):
        try:
            storeid = request.args.get("storeid")
            if not storeid:
                return {"message": "Missing 'storeid' parameter"}, 400

            db_connection = MysqlConnection()
            connection = db_connection.connect_mysql()
            cursor = connection.cursor()

            query = "SELECT addon_id, addon_name, addon_priority, areRequir, choices FROM addon WHERE store_id = %s"
            cursor.execute(query, (storeid,))
            addon_data = cursor.fetchall()

            cursor.close()
            connection.close()

            addon_list = []
            for row in addon_data:
                addon_dict = {
                    "addon_id": row[0],
                    "addon_name": row[1],
                    "addon_priority": row[2],
                    "areRequir": row[3],
                    "choices": json.loads(row[4]) if row[4] else [],
                }
                addon_list.append(addon_dict)

            return {"data": addon_list}, 200

        except Exception as e:
            return {
                "message": "An error occurred while retrieving addon data.",
                "error": str(e),
            }, 500

    def post(self):
        try:
            data = request.get_json()
            if (
                "storeid" in data
                and "addonName" in data
                and "addonRequir" in data
                and "choices" in data
            ):
                storeid = data.get("storeid")
                addonName = data.get("addonName")
                addonRequir = data.get("addonRequir")
                choices = data.get("choices")
                choices_json = json.dumps(choices)

                db_connection = MysqlConnection()
                connection = db_connection.connect_mysql()
                cursor = connection.cursor()

                query = "INSERT INTO addon (addon_name, store_id, areRequir, choices) VALUES (%s, %s, %s, %s)"
                cursor.execute(query, (addonName, storeid, addonRequir, choices_json))
                connection.commit()

                cursor.close()
                connection.close()

                return {"message": "Addon added successfully"}, 201

            return {
                "message": "Invalid request data. 'storeid', 'addonCatogolyName', 'addonRequir', and 'choices' are required."
            }, 400

        except Exception as e:
            return {
                "message": "An error occurred while processing the request.",
                "error": str(e),
            }, 500


@ns.route("/store/addon/<int:addon_id>")
class UpdateAddon(Resource):
    def put(self, addon_id):
        try:
            data = request.get_json()
            if "storeid" not in data:
                return {"message": "Missing 'storeid' in request data"}, 400

            storeid = data.get("storeid")
            addonName = data.get("addonName")
            addonRequir = data.get("addonRequir")
            choices = data.get("choices")
            choices_json = json.dumps(choices)

            db_connection = MysqlConnection()
            connection = db_connection.connect_mysql()
            cursor = connection.cursor()

            query = "UPDATE addon SET addon_name = %s, areRequir = %s, choices = %s WHERE addon_id = %s AND store_id = %s"
            cursor.execute(
                query, (addonName, addonRequir, choices_json, addon_id, storeid)
            )
            connection.commit()

            cursor.close()
            connection.close()

            return {"message": "Addon updated successfully"}, 200

        except Exception as e:
            return {
                "message": "An error occurred while processing the request.",
                "error": str(e),
            }, 500

    def delete(self, addon_id):
        try:
            data = request.get_json()
            if "storeid" not in data:
                return {"message": "Missing 'storeid' in request data"}, 400

            storeid = data.get("storeid")

            db_connection = MysqlConnection()
            connection = db_connection.connect_mysql()
            cursor = connection.cursor()

            query = "DELETE FROM addon WHERE addon_id = %s AND store_id = %s"
            cursor.execute(query, (addon_id, storeid))
            connection.commit()

            cursor.close()
            connection.close()

            return {"message": "Addon deleted successfully"}, 200

        except Exception as e:
            return {
                "message": "An error occurred while processing the request.",
                "error": str(e),
            }, 500


@ns.route("/store/addon/choice/<int:addon_id>")
class UpdateAddonChoice(Resource):
    def put(self, addon_id):
        try:
            data = request.get_json()
            choice_name = data.get("name")
            are_sale = data.get("areSale")

            db_connection = MysqlConnection()
            connection = db_connection.connect_mysql()
            cursor = connection.cursor()

            # Check if the choice exists in the addon's choices JSON column
            query = "SELECT addon_id, choices FROM addon WHERE addon_id = %s"
            cursor.execute(query, (addon_id,))
            result = cursor.fetchone()

            if result:
                addon_id, choices_json = result
                choices = json.loads(choices_json) if choices_json else []

                for choice in choices:
                    if choice.get("name") == choice_name:
                        # Update the "areSale" property for the matching choice
                        choice["areSale"] = are_sale

                # Update the choices back to the database
                updated_choices_json = json.dumps(choices)
                update_query = "UPDATE addon SET choices = %s WHERE addon_id = %s"
                cursor.execute(update_query, (updated_choices_json, addon_id))
                connection.commit()

            cursor.close()
            connection.close()

            return {"message": "Choice updated successfully"}, 200

        except Exception as e:
            return {
                "message": "An error occurred while updating the choice.",
                "error": str(e),
            }, 500


@ns.route("/store/menu")
class Menu(Resource):
    def post(self):
        try:
            required_fields = [
                "storeid",
                "menu_name",
                "menu_description",
                "menu_price",
                "menu_addon",
                "menu_menutype",
            ]
            missing_fields = [
                field for field in required_fields if field not in request.form
            ]
            if missing_fields:
                return {"error": f"Missing fields: {', '.join(missing_fields)}"}, 400

            db_connection = MysqlConnection()
            connection = db_connection.connect_mysql()
            cursor = connection.cursor()

            store_id = request.form["storeid"]
            menu_name = request.form["menu_name"]
            menu_description = request.form["menu_description"]
            menu_price = request.form["menu_price"]
            menu_addon = request.form["menu_addon"]
            menu_menutype = request.form["menu_menutype"]

            menu_addon = json.dumps(menu_addon)
            menu_menutype = json.dumps(menu_menutype)

            menu_description_stripped = menu_description.strip()
            if not menu_description_stripped:
                menu_description = ""

            if "foodImage" in request.files:
                menu_image = request.files["foodImage"].read()

                if menu_image.startswith(b"\x89PNG\r\n\x1a\n"):
                    image = Image.open(io.BytesIO(menu_image))
                    buffer = io.BytesIO()
                    image.convert("RGB").save(buffer, format="JPEG")
                    menu_image = buffer.getvalue()
            else:
                menu_image = None

            if "menu_id" in request.form:
                menu_id = request.form["menu_id"]

                # Remove old addon associations
                cursor.execute("DELETE FROM menu_addon WHERE menu_id = %s", (menu_id,))

                # Remove old menutype associations
                cursor.execute(
                    "DELETE FROM menu_menutype WHERE menu_id = %s", (menu_id,)
                )

                cursor.execute(
                    "UPDATE menu SET menu_image = %s, menu_name = %s, menu_description = %s, menu_price = %s, menu_addon = %s, menu_menutype = %s, store_id = %s WHERE menu_id = %s",
                    (
                        menu_image,
                        menu_name,
                        menu_description,
                        menu_price,
                        menu_addon,
                        menu_menutype,
                        store_id,
                        menu_id,
                    ),
                )
            else:
                cursor.execute(
                    "INSERT INTO menu (menu_image, menu_name, menu_description, menu_price, menu_addon, menu_menutype, store_id) VALUES (%s, %s, %s, %s, %s, %s, %s)",
                    (
                        menu_image,
                        menu_name,
                        menu_description,
                        menu_price,
                        menu_addon,
                        menu_menutype,
                        store_id,
                    ),
                )

                cursor.execute(
                    "SELECT menu_id FROM menu WHERE menu_name = %s AND menu_description = %s AND menu_price = %s AND store_id = %s",
                    (
                        menu_name,
                        menu_description,
                        menu_price,
                        store_id,
                    ),
                )
                row = cursor.fetchone()
                if row:
                    menu_id = row[0]
                else:
                    return {"message": "Missing when finding 'menu_id'"}, 400

            selected_addons = menu_addon.split(",")
            selected_addons = [(addon.strip('""')) for addon in selected_addons]
            selected_menu_types = menu_menutype.split(",")
            selected_menu_types = [
                (menu_type.strip('""')) for menu_type in selected_menu_types
            ]
            if selected_addons != [""]:
                addon_values = [(menu_id, addon_id) for addon_id in selected_addons]
                cursor.executemany(
                    "INSERT INTO menu_addon (menu_id, addon_id) VALUES (%s, %s)",
                    addon_values,
                )

            if selected_menu_types != [""]:
                menu_type_values = [
                    (menu_id, menu_type_id) for menu_type_id in selected_menu_types
                ]
                cursor.executemany(
                    "INSERT INTO menu_menutype (menu_id, menu_type_id) VALUES (%s, %s)",
                    menu_type_values,
                )
            connection.commit()

            cursor.close()
            connection.close()

            return {"message": "Save menu successful"}, 201
        except pymysql.Error as mysql_error:
            # Capture and display the MySQL error
            error_message = f"MySQL Error: {mysql_error}"
            print(error_message)

            return {
                "message": "An error occurred while processing the request.",
                "error": error_message,
            }, 500

        except Exception as e:
            return {
                "message": "An error occurred while processing the request.",
                "error": str(e),
            }, 500


@ns.route("/store/menu/<int:menu_id>")
class DeleteMenu(Resource):
    def delete(self, menu_id):
        try:
            # Check if the menu with the given ID exists
            db_connection = MysqlConnection()
            connection = db_connection.connect_mysql()
            cursor = connection.cursor()

            query = "SELECT * FROM menu WHERE menu_id = %s"
            cursor.execute(query, (menu_id))
            existing_menu = cursor.fetchone()

            if not existing_menu:
                cursor.close()
                connection.close()
                return {"message": "Menu not found"}, 404

            # Delete the menu and associated records (menu_addon and menu_menutype)
            cursor.execute("DELETE FROM menu WHERE menu_id = %s", (menu_id,))
            cursor.execute("DELETE FROM menu_addon WHERE menu_id = %s", (menu_id,))
            cursor.execute("DELETE FROM menu_menutype WHERE menu_id = %s", (menu_id,))

            connection.commit()
            cursor.close()
            connection.close()

            return {"message": "Menu deleted successfully"}, 200

        except Exception as e:
            return {
                "message": "An error occurred while processing the request.",
                "error": str(e),
            }, 500


@ns.route("/store/menus")
class MenuWithMenuType(Resource):
    def get(self):
        try:
            store_id = request.args.get("storeid")
            if not store_id:
                return {"message": "Missing 'storeid' parameter"}, 400

            db_connection = MysqlConnection()
            connection = db_connection.connect_mysql()
            cursor = connection.cursor()

            query = """
            SELECT
                mt.menu_type_id,
                mt.menu_type_name,
                mt.menu_type_priority,
                m.menu_id,
                m.menu_image,
                m.menu_name,
                m.menu_description,
                m.menu_price,
                m.menu_addon,
                m.menu_menutype
            FROM 
                menu_type mt
            LEFT JOIN 
                menu_menutype mm ON mt.menu_type_id = mm.menu_type_id
            LEFT JOIN 
                menu m ON mm.menu_id = m.menu_id
            WHERE
                mt.store_id = %s
            UNION
            SELECT
                0 AS menu_type_id,
                'ยังไม่ถูกจัดหมวดหมู่' AS menu_type_name,
                128 AS menu_type_priority,
                m.menu_id,
                m.menu_image,
                m.menu_name,
                m.menu_description,
                m.menu_price,
                m.menu_addon,
                m.menu_menutype
            FROM 
                menu m
            LEFT JOIN 
                menu_menutype mm ON m.menu_id = mm.menu_id
            WHERE
                m.store_id = %s AND mm.menu_type_id IS NULL;
            """
            cursor.execute(query, (store_id, store_id))
            menu_data = cursor.fetchall()
            cursor.close()
            connection.close()

            menu_list = []
            for row in menu_data:
                menu_type_id = row[0]
                menu_type_name = row[1]
                menu_type_priority = row[2]
                menu_item = {
                    "menu_id": row[3],
                    "menu_name": row[5],
                    "menu_description": row[6],
                    "menu_price": row[7],
                    "menu_addon": row[8],
                    "menu_menutype": row[9],
                }

                # Check if the menu_image is not None before encoding it.
                if row[4] is not None:
                    menu_item["menu_image"] = base64.b64encode(row[4]).decode("utf-8")

                menu_type = next(
                    (
                        item
                        for item in menu_list
                        if item["menu_type_name"] == menu_type_name
                    ),
                    None,
                )
                if menu_type is None:
                    menu_list.append(
                        {
                            "menu_type_id": menu_type_id,
                            "menu_type_name": menu_type_name,
                            "menu_type_priority": menu_type_priority,
                            "menu_items": [menu_item],
                        }
                    )
                else:
                    menu_type["menu_items"].append(menu_item)

            sorted_menu_list = sorted(
                menu_list, key=lambda x: (-x["menu_type_priority"], x["menu_type_id"])
            )

            return {"data": sorted_menu_list}, 200
        except Exception as e:
            return {
                "message": "An error occurred while retrieving menu data.",
                "error": str(e),
            }, 500


if __name__ == "__main__":
    app.run(debug=True)
