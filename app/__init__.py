from flask import Flask
from flask_restx import Api
from flask_cors import CORS

from .resources import ns


api = Api()


def create_app():
    app = Flask(__name__)
    CORS(app)

    api.init_app(app)
    api.add_namespace(ns)

    return app
