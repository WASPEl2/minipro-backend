from flask import Flask, send_file, jsonify, request, json
from flask_restx import reqparse, Api, Resource, Namespace
from flask_cors import CORS
import pymysql
from database import MysqlConnection

app = Flask(__name__)
CORS(app)
api = Api(app)

ns = Namespace("SmartCanteen")
ALLOWED_EXTENSIONS = {"png", "jpg"}





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

                query = "SELECT store_id FROM store WHERE (store_name = %s OR store_number = %s) AND store_pwd = %s"
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
            # Create an instance of the MysqlConnection class
            db_connection = MysqlConnection()

            # Connect to the MySQL database
            connection = db_connection.connect_mysql()

            # Create a cursor
            cursor = connection.cursor()

            # Execute a query to retrieve data from the "store" table
            query = "SELECT * FROM store"
            cursor.execute(query)

            # Fetch all rows from the result set
            store_data = cursor.fetchall()

            # Close the cursor and the database connection
            cursor.close()
            connection.close()

            # Convert the data to a list of dictionaries
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
