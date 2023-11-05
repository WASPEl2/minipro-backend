from flask import Flask
from flask_restx import reqparse, Api, Resource, Namespace
from flask_cors import CORS
import pymysql
from database import MysqlConnection

app = Flask(__name__)
CORS(app)
api = Api(app)

ns = Namespace("SmartCanteen")
ALLOWED_EXTENSIONS = {"png", "jpg"}


@ns.route("/register")
class Register(Resource):
    def post(self):
        # Create an instance of the MysqlConnection class
        db_connection = MysqlConnection()

        # Connect to the MySQL database
        connection = db_connection.connect_mysql()


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
