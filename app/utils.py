import requests
import json
import time
from os import remove, path
from flask import jsonify
from werkzeug.utils import secure_filename

from hashlib import md5
from app.settings import *
from app.Split import Split


def add_headers(response, status_code=200):
    response.headers.add('Access-Control-Allow-Origin', '*')  # To prevent Cors issues
    return response

def try_create_storage_file():
    if not path.exists("./app/server/static/files/"):
        makedirs("./app/server/static/files/")

def seconds_elapsed(start):
    """
    This method will return the difference between theese two dates

    :return:
    """
    done = time.time()
    elapsed = done - start
    return int(elapsed)


def get_direct_link(file_id):
    """

    :param file_id:
    :return:
    """
    print("[+] Fetching the direct link of the chunk file")

    # Now we fetch the tempory file path
    url2 = "https://api.telegram.org/bot" + TOKEN + "/getFile?file_id=" + file_id

    try:
        r2 = requests.get(url2)
        result2 = json.loads(r2.content.decode())
        return "https://api.telegram.org/file/bot" + TOKEN + "/" + result2["result"]["file_path"]
    except Exception as es:
        print("[x] An error occured, check your internet connection :", es)
        return None


def upload_chunk(chat_id, file_name):
    """
    This method will build the payload to be upload on telegram api

    :param chat_id:
    :param file_name:
    :return:
    """
    print("[+] Uploading the payload")
    url = "https://api.telegram.org/bot" + TOKEN + "/sendDocument"
    files = {
        'document': open(file_name, 'rb')
    }
    values = {
        'chat_id': chat_id
    }
    r = None
    try:
        r = requests.post(url, files=files, data=values)
    except Exception as es:
        print("[x] An error occured, check your internet connection :", es)

    return json.loads(r.content.decode())


def send_chunk(chat_id, chunk_name):
    """
        This method will send a file to the chat_id specified
    """
    print("[+] ---")
    print("[+] Sending chunk : ", chunk_name)

    # We upload the chunk and get the result as dict
    result = upload_chunk(chat_id, chunk_name)

    if result["ok"]:
        file_id = result["result"]["document"]["file_id"]
        print("[+] file_id : ", file_id)

        # Now we fetch the tempory file path from file_id
        direct_link = get_direct_link(file_id)
    else:
        file_id = False
        direct_link = "[x] Error, Operation failed !"

    return file_id, direct_link


def get_md5_sum(file_name):
    """
    This method only calcul the md5_sum of a file
    :param file_name:
    :return:
    """
    hasher = md5()
    with open(file_name, 'rb') as afile:
        buf = afile.read()
        hasher.update(buf)
    return hasher.hexdigest()


def send_all_chunks(chat_id, chunk_dir, final_map, json_map_of_chunks, delete_chunk=True):
    """

    :param delete_chunk:
    :param chat_id:
    :param chunk_dir:
    :param final_map:
    :param json_map_of_chunks:
    :return:
    """
    success = []  # chunks send successfully
    failed = []  # chunks failed

    for key, val in json_map_of_chunks.items():
        file_id, dr_link = send_chunk(chat_id, chunk_dir + val)
        if file_id is False:
            # We append the chunk as a failed
            failed.append({
                "id": key,
                "key": val
            })
        else:
            success.append({
                "id": key,
                "key": val
            })
            final_map["cloud_map"].append({
                "chunk_id": file_id,
                "chunk_name": val,
                "tmp_link": dr_link,
                "datetime": time.time()
            })
            # We delete/remove the chunk file if we are supposed to
            if delete_chunk:
                remove(chunk_dir + val)
                print("[+] Local chunk deleted successfully !")

    print("[+] -------------------------------------------------- ")
    print("[+] REPORTS !")
    print("[+] {} Succeed, {} Failed !".format(len(success), len(failed)))
    for elt in failed:
        print("[+] {}: {}".format(elt["id"], elt["key"]))
    print("[+] -------------------------------------------------- ")

    return success, failed, final_map


def send_file(chat_id, file_name):
    """

    :param chat_id:
    :param file_name:
    :return:
    """

    # We split the file using tth Split module
    # We instantiate the Split class by passing the chunk directory
    sp = Split(chunks_directory="./chunks/", json_map_directory="./json_maps/", data_directory="./app/server/static/files/")

    # We decompose the file in multiple chunks
    sp.decompose(file_name)

    # We get the md5-sum of the file
    md5_sum = get_md5_sum(file_name)

    # We build our final map
    final_map = {
        "file": {
            "file_path": file_name,
            "file_name": file_name.split("/")[-1]
        },
        "md5_sum": md5_sum,
        "cloud_map": [],  # The cloud json-map of all chunks
        "file_map": sp.get_map()  # The local json-map of all chunks
    }

    success, failed, final_map = send_all_chunks(chat_id, sp.chunks_directory, final_map, sp.get_map())

    # We set the map
    sp.set_map(final_map)

    # We write the json-map and return the path
    return sp.write_json_map(md5_sum)


def download_file(url, local_filename):
    """

    :param url:
    :param local_filename:
    :return:
    """
    print("[+] Downloading and saving in  ", local_filename)
    # NOTE the stream=True parameter below
    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        with open(local_filename, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192):
                if chunk:  # filter out keep-alive new chunks
                    f.write(chunk)
    return local_filename


def download_all_chunk(sp, the_map):
    """
    This method will download all the chunks present on the json_map
    :param sp:
    :param the_map:
    :return:
    """
    # We set the map
    sp.set_map(the_map)

    # For each chunk, we check it's date, if the tempory download link is down (date >= 2000) (600s -> 10mins)
    # then we refresh it
    # otherwise, we leave it as it
    print("[+] Fetching chunks...")
    for chk in the_map["cloud_map"]:
        elapsed_time = seconds_elapsed(chk["datetime"])
        print("[+] Elapsed_time: ", elapsed_time, "seconds")
        # time passed 33mins
        if elapsed_time >= 2000:
            # We need to refresh it
            # Now we fetch the tempory file path from file_id to get a new download_link
            print("[+] Refreshing the direct-link, the tmp_link looks obsolete !")
            file_id = chk["chunk_id"]
            chk["tmp_link"] = get_direct_link(file_id)

        # We download the chunk
        download_file(chk["tmp_link"], sp.chunks_directory + chk["chunk_name"])

    return sp


def md5_checker(sp, saving_path):
    """
    A simple md5 chekcer to tell if the integrity have been respected

    :param sp:
    :param saving_path:
    :return:
    """
    try:
        print("[+] md5_sum checking...")
        print("[+] Local md5 :", sp.get_map()["md5_sum"])
        print("[+] Remote md5 :", get_md5_sum(saving_path))
        # We check the md5 sha_sum
        if get_md5_sum(saving_path) == sp.get_map()["md5_sum"]:
            print("[+] md5_sum success match !")
        else:
            print("[x] md5_sum failed match !")

    except Exception as es:
        print("[x] Error when calculating the md5, please check again your file_path", es)


def get_file(json_map_path):
    """
    This method is for getting the list of chunk
    :param json_map_path:
    :return:
    """
    print("[+] Start getting the file...")

    # We read the json map
    with open(json_map_path, "r") as file_:
        the_map = json.loads(file_.read())
        # We check if the file exists
        if path.exists(the_map["file"]["file_path"]):
            return "static/files/" + the_map["file"]["file_name"]
        else:
            # We instantiate the Split class by passing the chunk directory
            sp = Split(chunks_directory="./chunks/", json_map_directory="./json_maps/", data_directory="./app/server/static/files/")
            
            # We download all the chunks
            sp = download_all_chunk(sp, the_map)

            # We rebuild the file
            saving_path = sp.data_directory + sp.get_map()["file"]["file_name"]
            sp.rebuild(saving_path)
            # We check the md5 of the file
            md5_checker(sp, saving_path)

            print("[+] Your file {} have been successfully rebuilded !".format(saving_path))

        return saving_path


def return_msg(status, message):
    return jsonify({
        'status': status,
        'message': message
    })

def proceed_file(file_, chat_id):
    if file_ and chat_id:
        if file_.filename == '':
            print('[x] No file selected for uploading !')
            return return_msg('error', 'No file selected for uploading !')
        else:
            print("[+] Uploading file in static !")
            filename = secure_filename(file_.filename)
            message = ""
            file_.save(path.join(UPLOAD_FOLDER, filename))
            json_path = "./json_maps/m_" + get_md5_sum(UPLOAD_FOLDER + filename).replace(" ", "").split("/")[-1] + ".json"

            if path.exists(json_path):
                # We don't save the file and return the json-map
                message = 'Your file ' + filename + ' was already saved on telegram servers!'
            else:
                # We save the file and return the json-map path
                json_path = send_file(chat_id, UPLOAD_FOLDER + filename)
                message = 'Your file ' + filename + ' have been saved successfully !'

            json_map_elt = json.loads(open(json_path).read())
            for cl_map in json_map_elt["cloud_map"]:
                del cl_map["tmp_link"]

            # We delete the original file
            remove(UPLOAD_FOLDER + filename)

            return jsonify({
                'status': 'success',
                'message': message,
                'file_key': json_path.split("/")[-1].split("_")[1].split(".")[0],
                'json_map': json_map_elt
            })
    else:
        print("[x] Some parameters are missing, check your request again !")
        return return_msg('error', 'Some parameters are missing, check your request again !')


def proceed_chunk(chunk, chat_id):
    if chunk and chat_id:
        if chunk.filename == '':
            print('[x] No file selected for uploading !')
            return return_msg('error', 'No file selected for uploading !')
        else:
            print("[+] Uploading file in static !")
            filename = secure_filename(chunk.filename)
            chunk.save(path.join(UPLOAD_FOLDER, filename))

            if upload_chunk(chat_id, UPLOAD_FOLDER + filename)["ok"]:
                return return_msg('success', 'Your chunk have been seend successfully !')
            else:
                return return_msg('error', 'Error, Operation failed, check again your parameters !')
    else:
        print("[x] Some parameters are missing, check your request again!")
        return return_msg('error', 'Some parameters are missing, check your request again !')

# For tests
# json_path = send_file("267092256", "/home/d4rk3r/Downloads/Telegram Desktop/video_2020-01-07_11-18-13.mp4")
# print("[+] json_path: ", json_path)
#
# # json_path = "/home/d4rk3r/ACTUALC/vagrant/PYTHON/github/json_maps/m_7cb6c6c955bd01948ce2b0fc218d6d05.json"
# get_file(json_path)
