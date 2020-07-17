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
        """[This method have the role on dividing multiple timethe global base64 string to optain the best ratio prime and content]

        Arguments:
            val {[type]} -- [description]

        Returns:
            [type] -- [description]
        """
        ancien_pri = self.maximum_size_per_chunk
        ancien_chunck = self.maximum_number_of_chunk

        return {"size": ancien_pri, "chunk": ancien_chunck}

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

            if not path.exists(self.data_directory):
                print("[+] Creating the datas dir")
                makedirs(self.data_directory)

            try:
                file_content_string = ""
                for i in range(0, len(map_)):
                    file_content_string += open(self.chunks_directory + map_[i], "r").read()
                    if delete_residuals:
                        remove(self.chunks_directory + map_[i])
                file_content = b64.b64decode(file_content_string)
                with open(final_path, "wb") as f:
                    f.write(file_content)
                print("[+] Remake done.")
            except Exception as e:
                print(e)
                print("[+] Remake went wrong.")
        except Exception as es:
            print(es)
            print("[+] Something went wrong, verify the path of your JSON map")

    def write_json_map(self, file_name):
        """
            This method will write on a json map
        """
        # We check if the directory chunks doesn't exist, then, we create it
        if not path.exists(self.json_map_directory):
            makedirs(self.json_map_directory)

        json_map_file_name = self.json_map_directory + "m_" + (file_name.replace(" ", "").split("/")[-1]) + ".json"
        with open(json_map_file_name, 'w+') as json_file_map:
            json.dump(self.map, json_file_map)
            print("[+] Map saved in '" + json_map_file_name + "'")
        return json_map_file_name

    def decompose(self, file_name):
        """
            This method decompose the file
        """
        print("[+] Decompose started...")
        with open(file_name, "rb") as image_file:

            # We check if the directory chunks doesn't exist, then, we create it
            if not path.exists(self.chunks_directory):
                makedirs(self.chunks_directory)

            to_print = b64.b64encode(image_file.read()).decode('utf-8')
            re_size = self.verify_size_content(self.divide(len(to_print)))

            i = 0
            print("\n[+] -----------")
            print("[+] Best divide ratio found !")
            print("[+] FILENAME : " + str(file_name))
            print("[+] FILE-SIZE : " + str(len(to_print)))

            while to_print:
                content = to_print[:re_size['chunk']]
                title = md5(content[:300].encode()).hexdigest()

                self.map[i] = title
                print("[+] CHUNK : " + title)
                # Optionnal, to saved the chunks
                with open(self.chunks_directory + title, "w+") as file_:
                    file_.write(content)
                # Optionnal, to saved the chunks
                to_print = to_print[re_size['chunk']:]
                i += 1
            print("[+] Decompose done.")
            # self.write_json_map(file_name)
            print("[+] -------")


if __name__ == "__main__":

    # Initialize the arguments
    # To decompose
    # python split.py -m cut -f /path/to/file
    # To rebuild your file
    # python split.py -m pull -f /path/to/reconstructed_file -j json_map.json
    prs = argparse.ArgumentParser()
    prs.add_argument('-m', '--mode', help='Split mode (pull/cut or p/c)', type=str)
    prs.add_argument('-f', '--file_name', help='File name to be compute (the file to decompose or to rebuild)',
                     required=True, type=str)
    prs.add_argument('-j', '--json_map', help='Json Map of the file', type=str)
    prs = prs.parse_args()

    # We instantiate and pass the path of the file we ant to split, the debug mode is just to see logs
    s = Split()

    if prs.mode.lower() == "cut" or prs.mode.lower() == "c":
        # We decompose the file in multiple chunks
        s.decompose(prs.file_name)
    elif (prs.mode.lower() == "pull" or prs.mode.lower() == "p") and prs.json_map is not None:
        # We rebuild the file
        s.rebuild(prs.json_map, delete_residuals=True)
    else:
        print("[x] Something went wrong, make sure to well provided parameters as specified")
