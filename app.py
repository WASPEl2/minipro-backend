from flask import Flask, request
from flask_restx import Api, Resource, fields
from datetime import datetime
from flask_cors import CORS
from PIL import Image
import base64
import io

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
class storeDetail(Resource):
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
class menutype(Resource):
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
class UpdateMenuType(Resource):
    def put(self, menuTypeid):
        try:
            data = request.get_json()

            if "menuType" in data:
                new_menu_type_name = data.get("menuType")

                db_connection = MysqlConnection()
                connection = db_connection.connect_mysql()
                cursor = connection.cursor()

                # Update the menu type name for the specified menuTypeid
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


if __name__ == "__main__":
    app.run(debug=True)
