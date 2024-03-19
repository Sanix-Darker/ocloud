import requests
import json
import time
import os
from os import remove, path
from flask import jsonify
from werkzeug.utils import secure_filename
from hashlib import md5
from ocloud.Split import Split
from ocloud.settings import TG_TOKEN, UPLOAD_FOLDER

# Constants
CHUNK_SIZE = 8192


def add_headers(response, status_code=200):
    response.headers.add("Access-Control-Allow-Origin", "*")  # To prevent Cors issues
    return response


def try_create_storage_file():
    os.makedirs("./ocloud/server/static/files/", exist_ok=True)


def seconds_elapsed(start):
    return int(time.time() - start)


def get_direct_link(file_id):
    url = f"https://api.telegram.org/bot{TG_TOKEN}/getFile?file_id={file_id}"
    try:
        result = json.loads(requests.get(url).content.decode())
        file_path = result.get("result", {}).get("file_path")
        return (
            f"https://api.telegram.org/file/bot{TG_TOKEN}/{file_path}"
            if file_path
            else None
        )
    except Exception as e:
        print("[x] An error occurred, check your internet connection:", e)
        return None


def upload_chunk(chat_id, file_name):
    url = f"https://api.telegram.org/bot{TG_TOKEN}/sendDocument"
    files = {"document": open(file_name, "rb")}
    values = {"chat_id": chat_id}
    try:
        response = requests.post(url, files=files, data=values)
        return json.loads(response.content.decode())
    except Exception as e:
        print("[x] An error occurred, check your internet connection:", e)
        return None


def send_chunk(chat_id, chunk_name):
    result = upload_chunk(chat_id, chunk_name)
    if result and result.get("ok"):
        file_id = result["result"]["document"]["file_id"]
        direct_link = get_direct_link(file_id)
    else:
        file_id = False
        direct_link = "[x] Error, Operation failed !"
    return file_id, direct_link


def get_md5_sum(file_name):
    hasher = md5()
    with open(file_name, "rb") as file:
        for chunk in iter(lambda: file.read(4096), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


def send_all_chunks(
    chat_id, chunk_dir, final_map, json_map_of_chunks, delete_chunk=True
):
    success = []
    failed = []
    for key, val in json_map_of_chunks.items():
        file_id, dr_link = send_chunk(chat_id, path.join(chunk_dir, val))
        if file_id is False:
            failed.append({"id": key, "key": val})
        else:
            success.append({"id": key, "key": val})
            final_map["cloud_map"].append(
                {
                    "chunk_id": file_id,
                    "chunk_name": val,
                    "tmp_link": dr_link,
                    "datetime": time.time(),
                }
            )
            if delete_chunk:
                remove(path.join(chunk_dir, val))
                print("[+] Local chunk deleted successfully !")
    print("[+] -------------------------------------------------- ")
    print("[+] REPORTS !")
    print("[+] {} Succeed, {} Failed !".format(len(success), len(failed)))
    for elt in failed:
        print("[+] {}: {}".format(elt["id"], elt["key"]))
    print("[+] -------------------------------------------------- ")
    return success, failed, final_map


def send_file(chat_id, file_name):
    sp = Split(
        chunks_directory="./chunks/",
        json_map_directory="./json_maps/",
        data_directory="./ocloud/server/static/files/",
    )
    sp.decompose(file_name)
    md5_sum = get_md5_sum(file_name)
    final_map = {
        "file": {"file_path": file_name, "file_name": file_name.split("/")[-1]},
        "md5_sum": md5_sum,
        "cloud_map": [],
        "file_map": sp.get_map(),
    }
    _, _, final_map = send_all_chunks(
        chat_id, sp.chunks_directory, final_map, sp.get_map()
    )
    sp.set_map(final_map)
    return sp.write_json_map(md5_sum)


def download_file(url, local_filename):
    with requests.get(url, stream=True) as response:
        response.raise_for_status()
        with open(local_filename, "wb") as file:
            for chunk in response.iter_content(chunk_size=CHUNK_SIZE):
                if chunk:
                    file.write(chunk)
    return local_filename


def download_all_chunk(sp, the_map):
    sp.set_map(the_map)
    print("[+] Fetching chunks...")
    for chk in the_map["cloud_map"]:
        elapsed_time = seconds_elapsed(chk["datetime"])
        print("[+] Elapsed_time: ", elapsed_time, "seconds")
        if elapsed_time >= 2000:
            print("[+] Refreshing the direct-link, the tmp_link looks obsolete !")
            chk["tmp_link"] = get_direct_link(chk["chunk_id"])
        download_file(
            chk["tmp_link"], path.join(sp.chunks_directory, chk["chunk_name"])
        )
    return sp


def md5_checker(sp, saving_path):
    try:
        print("[+] md5_sum checking...")
        print("[+] Local md5 :", sp.get_map()["md5_sum"])
        print("[+] Remote md5 :", get_md5_sum(saving_path))
        condition = get_md5_sum(saving_path) == sp.get_map()["md5_sum"]
        print("[+] md5_sum success match !") if condition else print(
            "[x] md5_sum failed match !"
        )
    except Exception as e:
        print(
            "[x] Error when calculating the md5, please check again your file_path", e
        )


def get_file(json_map_path):
    print("[+] Start getting the file...")
    with open(json_map_path, "r") as file:
        the_map = json.load(file)
        if path.exists(the_map["file"]["file_path"]):
            return "static/files/" + the_map["file"]["file_name"]
        else:
            sp = Split(
                chunks_directory="./chunks/",
                json_map_directory="./json_maps/",
                data_directory="./static/files/",
            )
            sp = download_all_chunk(sp, the_map)
            saving_path = sp.data_directory + sp.get_map()["file"]["file_name"]
            sp.rebuild(saving_path)
            md5_checker(sp, saving_path)
            print(
                "[+] Your file {} have been successfully rebuilt !".format(saving_path)
            )
        return saving_path


def return_msg(status, message):
    return jsonify({"status": status, "message": message})


def proceed_file(file_, chat_id):
    if file_ and chat_id:
        if file_.filename == "":
            print("[x] No file selected for uploading !")
            return return_msg("error", "No file selected for uploading !")
        else:
            print("[+] Uploading file in static !")
            filename = secure_filename(file_.filename)
            message = ""
            file_.save(path.join(UPLOAD_FOLDER, filename))
            json_path = (
                "./json_maps/m_"
                + get_md5_sum(UPLOAD_FOLDER + filename).replace(" ", "").split("/")[-1]
                + ".json"
            )
            if path.exists(json_path):
                message = (
                    "Your file " + filename + " was already saved on telegram servers!"
                )
            else:
                json_path = send_file(chat_id, UPLOAD_FOLDER + filename)
                message = "Your file " + filename + " have been saved successfully !"
            json_map_elt = json.loads(open(json_path).read())
            for cl_map in json_map_elt["cloud_map"]:
                del cl_map["tmp_link"]
            remove(UPLOAD_FOLDER + filename)
            return jsonify(
                {
                    "status": "success",
                    "message": message,
                    "file_key": json_path.split("/")[-1].split("_")[1].split(".")[0],
                    "json_map": json_map_elt,
                }
            )
    else:
        print("[x] Some parameters are missing, check your request again !")
        return return_msg(
            "error", "Some parameters are missing, check your request again !"
        )


def proceed_chunk(chunk, chat_id):
    if chunk and chat_id:
        if chunk.filename == "":
            print("[x] No file selected for uploading !")
            return return_msg("error", "No file selected for uploading !")
        else:
            print("[+] Uploading file in static !")
            filename = secure_filename(chunk.filename)
            chunk.save(path.join(UPLOAD_FOLDER, filename))
            if upload_chunk(chat_id, UPLOAD_FOLDER + filename)["ok"]:
                return return_msg(
                    "success", "Your chunk have been seend successfully !"
                )
            else:
                return return_msg(
                    "error", "Error, Operation failed, check again your parameters !"
                )
    else:
        print("[x] Some parameters are missing, check your request again!")
        return return_msg(
            "error", "Some parameters are missing, check your request again !"
        )
