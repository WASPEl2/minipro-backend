from tensorflow.keras.applications.efficientnet import preprocess_input
from tensorflow.keras.preprocessing.image import img_to_array
from flask import Flask, send_file, jsonify, request
from flask_restx import reqparse, Api, Resource, Namespace

from tensorflow import keras
from PIL import Image
import numpy as np
import base64
import json
import os
import io


ns = Namespace("api")

ALLOWED_EXTENSIONS = {"png", "jpg"}

herbs_json = os.path.join(os.path.dirname(__file__), "herbs.json")
history_json = os.path.join(os.path.dirname(__file__), "history.json")


model = keras.models.load_model("./model.h5")

image_upload_parser = reqparse.RequestParser()
image_upload_parser.add_argument(
    "image",
    type=str,
    required=True,
    help="Base64-encoded image data",
)


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in {
        "jpg",
        "jpeg",
        "png",
    }


@ns.route("/herbs/all")
class allHerbs(Resource):
    def get(self):
        try:
            with open(herbs_json, "r", encoding="utf-8") as json_file:
                data = json.load(json_file)
                return jsonify(data)
        except FileNotFoundError:
            return {"error": "JSON file not found"}, 404


@ns.route("/herbs/search/<string:name>")
class getHerbByName(Resource):
    def get(self, name):
        try:
            with open(herbs_json, "r", encoding="utf-8") as json_file:
                data = json.load(json_file)
                # Find the herb with the given name in the JSON data
                herb = next(
                    (item for item in data["data"] if item["herb_th_name"] == name),
                    None,
                )
                if herb:
                    return {"data": jsonify(herb)}
                else:
                    return {"error": "Herb not found"}, 404
        except FileNotFoundError:
            return {"error": "JSON file not found"}, 404


@ns.route("/herbs/id/<string:id>")
class getHerbById(Resource):
    def get(self, id):
        try:
            with open(herbs_json, "r", encoding="utf-8") as json_file:
                data = json.load(json_file)
                # Find the herb with the given ID in the JSON data
                herb = next(
                    (item for item in data["data"] if item["herb_id"] == id),
                    None,
                )
                if herb:
                    return {
                        "data": [herb]
                    }  # Wrap herb details in a list and a "data" key
                else:
                    return {"error": "Herb not found"}, 404
        except FileNotFoundError:
            return {"error": "JSON file not found"}, 404


from PIL import Image
import io


@ns.route("/herbs/predict")
class getHerbAnaly(Resource):
    def post(self):
        # Check if an image file is part of the request
        if "image" not in request.files:
            return {"error": "No image provided"}, 400

        # Get the uploaded image file
        image = request.files["image"]

        # Check if the file has a valid image extension (e.g., jpg, png)
        if image.filename == "":
            return {"error": "No image selected"}, 400
        if not allowed_file(image.filename):
            return {"error": "Invalid file format"}, 400

        try:
            # Read image data
            image_data = image.read()
            # Create an image object from the decoded data
            image_object = Image.open(io.BytesIO(image_data))

            if image_object.mode == "RGBA":
                image_object = image_object.convert("RGB")

            # Preprocess the image as needed
            image_object = image_object.resize((224, 224))
            image_array = img_to_array(image_object)
            image_array = preprocess_input(image_array)

            # Add batch dimension
            image_array = np.expand_dims(image_array, axis=0)

            # Make predictions using the trained model
            predictions = model.predict(image_array)

            # Get class labels and probabilities
            class_labels = {
                1: "ชะพลู",
                2: "ฟ้าทะลายโจร",
                3: "โหระพา",
                4: "กะเพรา",
                5: "มะนาว",
                6: "มะกรูด",
                7: "พลู",
                8: "สาบเสือ",
                9: "สะระแหน่",
                10: "ย่านาง  ",
            }

            # Convert predictions to class labels with probabilities and numerical labels
            class_probs = [
                {
                    "herb_id": i + 1,
                    "label": class_labels[i + 1],
                    "probability": float(prob),
                }
                for i, prob in enumerate(predictions[0])
            ]
            sorted_class_probs = sorted(
                class_probs, key=lambda x: x["probability"], reverse=True
            )

            top_4_ranking = sorted_class_probs[:4]
            print(top_4_ranking)

            # Create a ranking dictionary
            ranking = top_4_ranking

            return {"ranking": ranking}
        except Exception as e:
            print(str(e))
            return {"error": str(e)}, 500


@ns.route("/herbs/images/<string:image_name>")
class getHerbImage(Resource):
    def get(self, image_name):
        if allowed_file(image_name):
            current_directory = os.path.dirname(__file__)
            images_directory = os.path.join(current_directory, "assets", "images")
            image_path = os.path.join(images_directory, image_name)
            if os.path.exists(image_path):
                return send_file(image_path)
            elif not os.path.exists(images_directory):
                return {"error": "Invalid file path"}, 404
            else:
                return {"error": "Image not found"}, 404
        else:
            return {"error": "Invalid file extension"}, 400
