from flask import Flask, request
from flask_restx import Api, Resource, fields
from flask_cors import CORS
from PIL import Image
import io
from database import MysqlConnection

app = Flask(__name__)
CORS(app)
api = Api(app)

ns = api.namespace("SmartCanteen")
ALLOWED_EXTENSIONS = {"png", "jpg"}


@app.route("/")
class Home(Resource):
    def get(self):
        return {"message": "Welcome to the SmartCanteen API!"}, 200


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
                qrcode_image = Image.open(io.BytesIO(qrcode_image))

            else:
                qrcode_image = None

            if "storeImage" in request.files:
                store_image = request.files["storeImage"].read()
                store_image = Image.open(io.BytesIO(store_image))

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

            return {"message": "Store registration successful"}, 200

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


@ns.route("/store")
class StoreData(Resource):
    def get(self):
        try:
            db_connection = MysqlConnection()
            connection = db_connection.connect_mysql()
            cursor = connection.cursor()

            query = "SELECT * FROM store"
            cursor.execute(query)
            store_data = cursor.fetchall()
            cursor.close()
            connection.close()

            store_list = []
            for row in store_data:
                store_dict = {
                    "store_name": row[0],
                    "store_owner": row[1],
                    "store_number": row[2],
                    "store_pwd": row[3],
                    "store_type": row[4],
                    "store_locate": row[5],
                }
                store_list.append(store_dict)

            # Return the retrieved data as JSON response
            return store_list, 200
        except Exception as e:
            return {
                "message": "An error occurred while retrieving data.",
                "error": str(e),
            }, 500


if __name__ == "__main__":
    app.run(debug=True)
