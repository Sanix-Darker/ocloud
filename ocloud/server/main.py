# coding: utf-8
import json
from flask import Flask, jsonify, request, render_template, send_file as send_file_flask
from flask_cors import CORS, cross_origin
from os import path, listdir

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


@app.route("/")
def index():
    try_create_storage_file()
    return render_template("index.html")


@app.route("/api/", methods=["GET"])  # To prevent Cors issues
@cross_origin(supports_credentials=True)
def api():
    try_create_storage_file()
    # Build the response
    response = jsonify(
        {
            "status": "success",
            "author": "sanix-darker (github.com/sanix-darker)",
            "documentation": "https://documenter.getpostman.com/view/2696027/SzYgRaw1?version=latest",
            "message": "Welcome to Ocloud API.",
        }
    )
    return add_headers(response)


@app.route("/api/count", methods=["GET"])  # To prevent Cors issues
@cross_origin(supports_credentials=True)
def cunt_files():
    # Build the response
    response = jsonify({"status": "success", "count": len(listdir("./json_maps/"))})
    return add_headers(response)


@app.route("/api/checkfile/<file_key>", methods=["GET"])  # To prevent Cors issues
@cross_origin(supports_credentials=True)
def check_files(file_key):
    # Build the response
    json_file = "m_" + file_key + ".json"
    if path.exists("./json_maps/" + json_file):
        file_ = json.loads(open("./json_maps/" + json_file).read())
        response = {
            "status": "success",
            "file_name": file_["file"]["file_name"],
            "chunks": len(file_["cloud_map"]),
        }
    else:
        response = {
            "status": "error",
            "message": "This file-key doesn't exist in the server, it can not be regenerated !",
        }

    return add_headers(jsonify(response))


@app.route("/api/file/<file_key>", methods=["GET"])
@cross_origin(supports_credentials=True)
def getFiles(file_key):
    try_create_storage_file()

    json_map_file = "./json_maps/m_" + file_key + ".json"
    if not path.exists(json_map_file):
        print("[x] This json_map doesn't exist in the server !")
        # Build the response
        response = jsonify(
            {
                "status": "error",
                "file_key": file_key,
                "message": "This json_map doesn't exist in the server !",
            }
        )
        return add_headers(response)
    else:
        file_path = get_file(json_map_file)
        return send_file_flask(file_path, as_attachment=True)


@app.route("/api/uploadchunk", methods=["POST"])  # To prevent Cors issues
@cross_origin(supports_credentials=True)
def apiUploadChunk():
    chunk = request.files["chunk"]
    chat_id = request.form.get("chat_id")
    try_create_storage_file()

    try:
        response = proceed_chunk(chunk, chat_id)
    except Exception as es:
        print("[x] err: ", es)
        response = return_msg(
            "error", "An error occur on the server, check again your requirements !"
        )

    return add_headers(response)


@app.route("/api/upload", methods=["POST"])
@cross_origin(supports_credentials=True)
def apiUpload():
    response = {}
    try_create_storage_file()

    try:
        chat_id = request.form.get("chat_id")
        file_ = request.files["file"]
        response = proceed_file(file_, chat_id)
    except Exception as es:
        print(es)
        response = return_msg(
            "error",
            "Request Entity Too Large: The data value transmitted exceeds the capacity limit !",
        )

    return add_headers(response)

if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=False, port=9432)
