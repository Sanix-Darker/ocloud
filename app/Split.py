#
#  ____  ____  _     ___ _____
# / ___||  _ \| |   |_ _|_   _|
# \___ \| |_) | |    | |  | |
#  ___) |  __/| |___ | |  | |
# |____/|_|   |_____|___| |_|
# - - - - - - - - - - - - - - -
# A module to decompose and reMake a file based on a map and chuncks
# By Sanix-darker
#

import base64 as b64
from hashlib import md5
from os import remove, path, makedirs
import json
import argparse


class Split:

    def __init__(self, chunks_directory="./chunks/", json_map_directory="./json_maps/", data_directory="./datas/",
                 maximum_size_per_chunk=15000000, minimum_number_of_chunk=3, maximum_number_of_chunk=99999):
        self.data_directory = data_directory
        self.json_map_directory = json_map_directory
        self.chunks_directory = chunks_directory
        self.maximum_size_per_chunk = maximum_size_per_chunk
        self.minimum_number_of_chunk = minimum_number_of_chunk
        self.maximum_number_of_chunk = maximum_number_of_chunk
        self.map = {}
        # self.chunk_array = []

    # Getter/setter for map
    def get_map(self):
        return self.map

    def set_map(self, m):
        self.map = m

    def divide(self, val):
        """
            This method have the role on dividing multiple timethe global base64 string to optain the best ratio prime and content
        """
        return {
            "size": self.maximum_size_per_chunk,
            "chunk": self.maximum_number_of_chunk
        }

    def create_dir(self, dir_):
        if not path.exists(dir_):
            makedirs(dir_)

    def verify_size_content(self, re_size):
        """
            We just need to make sure the number of size never > content per chunk

        Arguments:
            re_size {[type]} -- [description]

        Returns:
            [type] -- [description]
        """
        if re_size['chunk'] < re_size['size']:
            to_alternate = re_size['chunk']
            re_size['chunk'] = re_size['size']
            re_size['size'] = to_alternate
        return re_size

    def rebuild(self, final_path, delete_residuals=False):
        """
        This method reconstruct the file

        Arguments:
            final_path {[type]} -- [description]
            map_ {[type]} -- [description]
            chunk_path {[type]} -- [description]
        """
        try:
            map_ = self.map["file_map"]
            map_ = {int(k): v for k, v in map_.items()}
            print("[+] Rebuild started...")

            self.create_dir(self.data_directory)

            try:
                ff = bytes()
                for chk in map_:
                    cmp_path = self.chunks_directory + map_[chk]
                    with open(cmp_path, 'rb') as f:
                        ff += f.read()
                    if delete_residuals:
                        remove(cmp_path)
                with open(final_path, 'wb') as infile:
                    infile.write(ff)
                print("[+] Remake done.")
            except Exception as e:
                print("[+] Remake went wrong, ", e)
        except Exception as es:
            print("[+] Something went wrong, verify the path of your JSON map, ", es)

    def write_json_map(self, file_name):
        """
            This method will write on a json map
        """
        # We check if the directory chunks doesn't exist, then, we create it
        self.create_dir(self.json_map_directory)

        json_map_file_name = self.json_map_directory + "m_" + (file_name.replace(" ", "").split("/")[-1]) + ".json"
        with open(json_map_file_name, 'w+') as json_file_map:
            json.dump(self.map, json_file_map)
            print("[+] Map saved in '" + json_map_file_name + "'")
        return json_map_file_name

    def decompose(self, file_name):
        """
            This method decompose the file
        """
        # We check if the directory chunks doesn't exist, then, we create it
        self.create_dir(self.chunks_directory)

        re_size = {}
        print("[+] Decompose started...")
        with open(file_name, 'rb') as infile:
            divide = self.divide(str(infile.read()).replace("b'", "").replace("'", ""))
            re_size = self.verify_size_content(divide)

        with open(file_name, 'rb') as infile:
            i = 0
            while True:
                chunk = infile.read(int(re_size['chunk']))

                if not chunk:
                    break
                self.map[i] = md5(chunk).hexdigest()

                with open(self.chunks_directory + self.map[i], "wb") as file_to:
                    file_to.write(chunk)
                i += 1
        print("[+] Decompose done.")

