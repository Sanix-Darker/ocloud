# coding: utf-8
import os
import json
from flask import Flask, jsonify, request, render_template, send_file
from flask_cors import CORS, cross_origin

from ocloud.settings import UPLOAD_FOLDER
from ocloud.utils import (
    add_headers,
    get_file,
    proceed_chunk,
    proceed_file,
    return_msg,
    try_create_storage_file,
)

app = Flask(__name__)
CORS(app, support_credentials=True)

app.config["Secret"] = "Secret"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["MAX_CONTENT_LENGTH"] = 100 * 1024 * 1024

JSON_MAPS_FOLDER = "./json_maps/"

def build_response(data, status="success", **kwargs):
    response_data = {"status": status, **data, **kwargs}
    return jsonify(response_data)

@app.route("/")
def index():
    try_create_storage_file()
    return render_template("index.html")

@app.route("/api/", methods=["GET"])
@cross_origin(supports_credentials=True)
def api():
    try_create_storage_file()
    data = {
        "author": "sanix-darker (github.com/sanix-darker)",
        "documentation": "https://documenter.getpostman.com/view/2696027/SzYgRaw1?version=latest",
        "message": "Welcome to Ocloud API.",
    }
    return add_headers(build_response(data))

@app.route("/api/count", methods=["GET"])
@cross_origin(supports_credentials=True)
def count_files():
    count = len(os.listdir(JSON_MAPS_FOLDER))
    return add_headers(build_response({"count": count}))

@app.route("/api/checkfile/<file_key>", methods=["GET"])
@cross_origin(supports_credentials=True)
def check_file(file_key):
    json_file = f"m_{file_key}.json"
    file_path = os.path.join(JSON_MAPS_FOLDER, json_file)

    if os.path.exists(file_path):
        with open(file_path) as f:
            file_data = json.load(f)
        response_data = {
            "file_name": file_data["file"]["file_name"],
            "chunks": len(file_data["cloud_map"]),
        }
        return add_headers(build_response(response_data))
    else:
        return add_headers(build_response({"message": "File not found."}, status="error"))

@app.route("/api/file/<file_key>", methods=["GET"])
@cross_origin(supports_credentials=True)
def get_file_from_key(file_key):
    try_create_storage_file()
    json_map_file = f"./json_maps/m_{file_key}.json"

    if not os.path.exists(json_map_file):
        return add_headers(build_response({"file_key": file_key, "message": "File not found."}, status="error"))
    else:
        file_path = get_file(json_map_file)
        if os.path.exists(file_path):
            return send_file(file_path.replace("./ocloud/server/", ""), as_attachment=True)
        else:
            return render_template("refreshing.html")

@app.route("/api/uploadchunk", methods=["POST"])
@cross_origin(supports_credentials=True)
def upload_chunk():
    chunk = request.files["chunk"]
    chat_id = request.form.get("chat_id")
    try_create_storage_file()

    try:
        response = proceed_chunk(chunk, chat_id)
    except Exception as es:
        response = return_msg("error", "An error occurred on the server. Please check your requirements.")

    return add_headers(response)

@app.route("/api/upload", methods=["POST"])
@cross_origin(supports_credentials=True)
def upload():
    try_create_storage_file()

    try:
        chat_id = request.form.get("chat_id")
        file_ = request.files["file"]
        response = proceed_file(file_, chat_id)
    except Exception as es:
        response = return_msg("error", "Request Entity Too Large: The data value transmitted exceeds the capacity limit.")

    return add_headers(response)

if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=False, port=9432)
