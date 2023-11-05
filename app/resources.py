from flask import Flask
from flask_restx import reqparse, Api, Resource, Namespace
from flask_cors import CORS
import pymysql

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


if __name__ == "__main__":
    app.run(debug=True)
