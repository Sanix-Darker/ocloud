from typing import Any
import requests
import json
import time
import os
from os import remove, path
from hashlib import md5
from ocloud.Split import Split
from ocloud.settings import TG_TOKEN, UPLOAD_FOLDER
import logging
import re
import unicodedata

_LOGGER = logging.getLogger(__name__)
CHUNK_SIZE = 8192


def secure_filename(filename, allowed_extensions=None):
    """
    Secure a filename for storing on the filesystem.

    Args:
        filename (str): The filename to secure.
        allowed_extensions (list): List of allowed file extensions.

    Returns:
        str: Secured filename.
    """
    if not filename:
        raise ValueError("Empty filename")

    filename = unicodedata.normalize("NFKD", filename)
    filename = filename.encode("ascii", "ignore").decode("ascii")
    # Remove any characters that are not alphanumeric, underscores, or hyphens
    filename = re.sub(r"[^\w.-]", "_", filename).strip()
    # Ensure filename does not start with a dot or contain multiple dots in a row
    filename = re.sub(r"\.+", ".", filename)
    if filename.startswith("."):
        filename = "_" + filename
    # If allowed_extensions is provided, ensure the filename has a valid extension
    if allowed_extensions:
        filename, extension = os.path.splitext(filename)
        if not extension or extension[1:] not in allowed_extensions:
            raise ValueError("Invalid file extension")

    return filename


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
        _LOGGER.warning("[x] An error occurred, check your internet connection:", e)
        return None


def upload_chunk(chat_id, file_name) -> dict:
    url = f"https://api.telegram.org/bot{TG_TOKEN}/sendDocument"
    files = {"document": open(file_name, "rb")}
    values = {"chat_id": chat_id}
    try:
        response = requests.post(url, files=files, data=values)
        return json.loads(response.content.decode())
    except Exception as e:
        _LOGGER.warning("[x] An error occurred, check your internet connection:", e)
        return {}


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
                _LOGGER.info("[+] Local chunk deleted successfully !")
    _LOGGER.info("[+] -------------------------------------------------- ")
    _LOGGER.info("[+] REPORTS !")
    _LOGGER.info("[+] {} Succeed, {} Failed !".format(len(success), len(failed)))
    for elt in failed:
        _LOGGER.info("[+] {}: {}".format(elt["id"], elt["key"]))
    _LOGGER.info("[+] -------------------------------------------------- ")
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
    success, _, final_map = send_all_chunks(
        chat_id, sp.chunks_directory, final_map, sp.get_map()
    )
    sp.set_map(final_map)
    if success:  # If at least one chunk was successfully sent
        return sp.write_json_map(md5_sum)

    return None


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
    _LOGGER.info("[+] Fetching chunks...")
    for chk in the_map["cloud_map"]:
        elapsed_time = seconds_elapsed(chk["datetime"])
        _LOGGER.info("[+] Elapsed_time: %s seconds", elapsed_time)
        if elapsed_time >= 2000:
            _LOGGER.info(
                "[+] Refreshing the direct-link, the tmp_link looks obsolete !"
            )
            chk["tmp_link"] = get_direct_link(chk["chunk_id"])
        download_file(
            chk["tmp_link"], path.join(sp.chunks_directory, chk["chunk_name"])
        )
    return sp


def md5_checker(sp, saving_path):
    """ """
    try:
        _LOGGER.info("[+] md5_sum checking...")
        _LOGGER.info("[+] Local md5 :", sp.get_map()["md5_sum"])
        _LOGGER.info("[+] Remote md5 :", get_md5_sum(saving_path))
        condition = get_md5_sum(saving_path) == sp.get_map()["md5_sum"]
        _LOGGER.info("[+] md5_sum success match !") if condition else print(
            "[x] md5_sum failed match !"
        )
    except Exception as e:
        _LOGGER.error(
            "[x] Error when calculating the md5, please check again your file_path", e
        )


def get_file(json_map_path: str) -> str:
    """ """
    _LOGGER.info("[+] Start getting the file...")
    with open(json_map_path, "r") as file:
        the_map = json.load(file)
        file_path = the_map["file"]["file_path"]
        if path.exists(file_path):
            return "static/files/" + the_map["file"]["file_name"]

        sp = Split(
            chunks_directory="./chunks/",
            json_map_directory="./json_maps/",
            data_directory="./ocloud/server/static/files/",
        )
        sp = download_all_chunk(sp, the_map)
        saving_path = sp.data_directory + sp.get_map()["file"]["file_name"]
        sp.rebuild(saving_path)
        md5_checker(sp, saving_path)
        _LOGGER.info(
            "[+] Your file {} has been successfully rebuilt !".format(saving_path)
        )
        return saving_path


def proceed_file(file_, chat_id: str) -> tuple[str, str | Any]:
    """ """
    if not file_ or not chat_id:
        _LOGGER.info("[x] Some parameters are missing, check your request again !")
        return ("error", "Some parameters are missing, check your request again !")

    if file_.filename == "":
        _LOGGER.info("[x] No file selected for uploading !")
        return ("error", "No file selected for uploading !")

    _LOGGER.info("[+] Uploading file in static !")
    filename = secure_filename(file_.filename)
    file_path = path.join(UPLOAD_FOLDER or "", filename)

    try:
        file_.save(file_path)
    except Exception as e:
        _LOGGER.error(f"Failed to save the file: {e}")
        return ("error", "Failed to save the file")

    json_path = (
        f"./json_maps/m_{get_md5_sum(file_path).replace(' ', '').split('/')[-1]}.json"
    )

    if path.exists(json_path):
        message = f"Your file {filename} was already saved on telegram servers!"
    else:
        json_path = send_file(chat_id, file_path)
        message = f"Your file {filename} have been saved successfully !"

    assert json_path is not None
    try:
        json_map_elt = json.loads(open(json_path).read())
        for cl_map in json_map_elt.get("cloud_map", []):
            del cl_map["tmp_link"]
    except Exception as e:
        _LOGGER.error(f"Failed to process JSON map: {e}")
        return ("error", "Failed to process JSON map")

    try:
        os.remove(file_path)
    except Exception as e:
        _LOGGER.error(f"Failed to remove the file: {e}")
        return ("error", "Failed to remove the file")

    return (
        "success",
        {
            "message": message,
            "file_key": json_path.split("/")[-1].split("_")[1].split(".")[0],
            "json_map": json_map_elt,
        },
    )


def proceed_chunk(chunk, chat_id) -> tuple[str, Any]:
    if not chunk or not chat_id:
        return ("error", "Some parameters are missing, check your request again!")

    if chunk.filename == "":
        return ("error", "No file selected for uploading!")

    filename = secure_filename(chunk.filename)
    chunk.save(os.path.join(UPLOAD_FOLDER, filename))

    if upload_chunk(chat_id, UPLOAD_FOLDER + filename).get("ok"):
        return ("success", "Your chunk has been successfully sent!")
    else:
        return ("error", "Error: Operation failed. Please check your parameters.")
