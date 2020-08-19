# coding: utf-8
from flask import Flask, jsonify, request, render_template, send_file as send_file_flask
from flask_cors import CORS, cross_origin
from werkzeug.utils import secure_filename
from os import path, makedirs, remove, listdir
from app.utils import *
from app.settings import *

app = Flask(__name__)
CORS(app, support_credentials=True)

app.config['Secret'] = "Secret"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024


@app.route("/")
def index():
    try_create_storage_file()
    return render_template("index.html");  


@app.route('/api/', methods=['GET'])  # To prevent Cors issues
@cross_origin(supports_credentials=True)
def api():
    try_create_storage_file()
    # Build the response
    response = jsonify({
        'status': 'success',
        'author': 'sanix-darker (github.com/sanix-darker)',
        'documentation': 'https://documenter.getpostman.com/view/2696027/SzYgRaw1?version=latest',
        'message': 'Welcome to Ogram API.'
    })
    return add_headers(response)


@app.route('/api/count', methods=['GET'])  # To prevent Cors issues
@cross_origin(supports_credentials=True)
def cunt_files():
    # Build the response
    response = jsonify({
        'status': 'success',
        'count': len(listdir("./json_maps/"))
    })
    return add_headers(response)


@app.route('/api/file/<file_key>', methods=['GET'])
@cross_origin(supports_credentials=True)
def getFiles(file_key):
    try_create_storage_file()
        
    json_map_file = "./json_maps/m_" + file_key + ".json"
    if not path.exists(json_map_file):
        print("[x] This json_map doesn't exist in the server !")
        # Build the response
        response = jsonify({'status': 'error',
                            "file_key": file_key,
                            'message': "This json_map doesn't exist in the server !"})
        return add_headers(response)
    else:
        try:
            file_path = get_file(json_map_file)
            if path.exists("./app/server/" + file_path):
                return send_file_flask(path.join(file_path), as_attachment=True)
            else:
                return render_template("refreshing.html")
        except Exception as es:
            return render_template("refreshing.html")


@app.route('/api/uploadchunk', methods=['POST'])  # To prevent Cors issues
@cross_origin(supports_credentials=True)
def apiUploadChunk():
    chunk = request.files['chunk']
    chat_id = request.form.get("chat_id")
    try_create_storage_file()

    try:
        response = proceed_chunk(chunk, chat_id)
    except Exception as es:
        print("[x] err: ", es)
        response = return_msg('error', 'An error occur on the server, check again your requirements !')

    return add_headers(response)


@app.route('/api/upload', methods=['POST'])
@cross_origin(supports_credentials=True)
def apiUpload():
    response = {}
    try_create_storage_file()

    try:
        chat_id = request.form.get("chat_id")
        file_ = request.files['file']
        response = proceed_file(file_, chat_id)
    except Exception as es:
        print(es)
        response = return_msg('error',
                              'Request Entity Too Large: The data value transmitted exceeds the capacity limit !')

    return add_headers(response)


@app.route('/api/download/<file_key>', methods=['GET'])  # To prevent Cors issues
@cross_origin(supports_credentials=True)
def apiDownload(file_key):
    json_map_file = "./json_maps/m_" + file_key + ".json"
    if not path.exists(json_map_file):
        print("[x] This json_map doesn't exist in the server !")
        # Build the response
        response = jsonify({'status': 'error',
                            "file_key": file_key,
                            'message': "This json_map doesn't exist in the server !"})
    else:
        saving_path = get_file(json_map_file)
        # Build the response
        response = jsonify({'status': 'success',
                            "file_key": file_key,
                            'message': 'file restored successfully !',
                            'download_link': request.host_url + "api/file/" + file_key})
    return add_headers(response)


if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True, port=9432)
