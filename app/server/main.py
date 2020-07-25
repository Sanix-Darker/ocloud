# coding: utf-8
from flask import Flask, jsonify, request, render_template, send_file as send_file_flask
from flask_cors import CORS, cross_origin
from werkzeug.utils import secure_filename
from os import path, makedirs, remove, listdir
from app.utils import *

app = Flask(__name__)
# CORS(app, support_credentials=True)

app.config['Secret'] = "Secret"
app.config['UPLOAD_FOLDER'] = "./app/server/static/files/"
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024

if not path.exists("./app/server/static/files/"):
    makedirs("./app/server/static/files/")



@app.route("/")
def index():
    return render_template("index.html");  


@app.route('/api/', methods=['GET'])  # To prevent Cors issues
# @cross_origin(supports_credentials=True)
def api():
    # Build the response
    response = jsonify({
        'status': 'success',
        'author': 'sanix-darker (github.com/sanix-darker)',
        'documentation': 'https://documenter.getpostman.com/view/2696027/SzYgRaw1?version=latest',
        'message': 'Welcome to Ogram API.'
    })
    # Let's allow all Origin requests
    response.headers.add('Access-Control-Allow-Origin', '*')  # To prevent Cors issues
    return response


@app.route('/api/count', methods=['GET'])  # To prevent Cors issues
# @cross_origin(supports_credentials=True)
def cunt_files():
    # Build the response
    response = jsonify({
        'status': 'success',
        'count': len(listdir("./json_maps/"))
    })
    # Let's allow all Origin requests
    response.headers.add('Access-Control-Allow-Origin', '*')  # To prevent Cors issues
    return response


@app.route('/api/file/<file_key>', methods=['GET'])  # To prevent Cors issues
# @cross_origin(supports_credentials=True)
def getFiles(file_key):
    json_map_file = "./json_maps/m_" + file_key + ".json"
    if not path.exists(json_map_file):
        print("[x] This json_map doesn't exist in the server !")
        # Build the response
        response = jsonify({'status': 'error',
                            "file_key": file_key,
                            'message': "This json_map doesn't exist in the server !"})
        return response
    else:
        file_path = get_file(json_map_file)
        if (path.exists("./app/server/" + file_path)):
            return send_file_flask(path.join(file_path), as_attachment=True)
        else:
            return render_template("refreshing.html")


@app.route('/api/uploadchunk', methods=['POST'])  # To prevent Cors issues
# @cross_origin(supports_credentials=True)
def apiUploadChunk():
    chunk = request.files['chunk']
    chat_id = request.form.get("chat_id")

    try:
        if chunk and chat_id:
            if chunk.filename == '':
                print('[x] No file selected for uploading !')
                response = jsonify({
                    'status': 'error', 
                    'message': 'No file selected for uploading !'
                })
            else:
                print("[+] Uploading file in static !")
                filename = secure_filename(chunk.filename)
                chunk.save(path.join(app.config['UPLOAD_FOLDER'], filename))

                result = upload_chunk(chat_id, app.config['UPLOAD_FOLDER'] + filename)
                if result["ok"]:
                    response = jsonify({
                        'status': 'success',
                        'message': 'Your chunk have been seend successfully !'
                    })
                else:
                    response = jsonify({
                        'status': 'error',
                        'message': 'Error, Operation failed, check again your parameters !'
                    })
        else:
            print("[x] Some parameters are missing, check your request again!")
            response = jsonify({
                "status": "error",
                "message": "Some parameters are missing, check your request again !"
            })
    except Exception as es:
        print("[x] err: ", es)
        response = jsonify({
            "status": "error",
            "message": "An error occur on the server, check again your requirements !"
        })

    # Let's allow all Origin requests
    response.headers.add('Access-Control-Allow-Origin', '*')  # To prevent Cors issues
    return response


@app.route('/api/upload', methods=['POST'])  # To prevent Cors issues
# @cross_origin(supports_credentials=True)
def apiUpload():
    try:
        chat_id = request.form.get("chat_id")
        file_ = request.files['file']
        response = {}

        if file_ and chat_id:
            if file_.filename == '':
                print('No file selected for uploading !')
                response = jsonify({'status': 'error', 'message': 'No file selected for uploading !'})

            else:
                print("[+] Uploading file in static !")
                filename = secure_filename(file_.filename)

                message = ""
                file_.save(path.join(app.config['UPLOAD_FOLDER'], filename))
                json_path = "./json_maps/m_" + get_md5_sum("./app/server/static/files/" + filename).replace(" ", "").split("/")[-1] + ".json"

                if path.exists(json_path):
                    # We don't save the file and return the json-map
                    message = 'Your file ' + filename + ' was already saved on telegram servers!'
                else:
                    # We save the file and return the json-map path
                    json_path = send_file(chat_id, "./app/server/static/files/" + filename)
                    message = 'Your file ' + filename + ' have been saved successfully !'

                json_map_elt = json.loads(open(json_path).read())
                for cl_map in json_map_elt["cloud_map"]:
                    del cl_map["tmp_link"]

                response = jsonify({
                    'status': 'success',
                    'message': message,
                    'file_key': json_path.split("/")[-1].split("_")[1].split(".")[0],
                    'json_map': json_map_elt
                })
                # We delete the original file
                remove("./app/server/static/files/" + filename)
        else:
            print("[x] Some parameters are missing, check your request again!")
            response = jsonify({
                "status": "error",
                "message": "Some parameters are missing, check your request again !"
            })

    except Exception as es:
        print(es)
        response = jsonify({
            "status": "error",
            "message": "Request Entity Too Large: The data value transmitted exceeds the capacity limit.!"
        })

    # Let's allow all Origin requests
    response.headers.add('Access-Control-Allow-Origin', '*')  # To prevent Cors issues
    return response


@app.route('/api/download/<file_key>', methods=['GET'])  # To prevent Cors issues
# @cross_origin(supports_credentials=True)
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
    # Let's allow all Origin requests
    response.headers.add('Access-Control-Allow-Origin', '*')  # To prevent Cors issues
    return response


if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True, port=9432)
