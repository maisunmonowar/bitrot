import os
import json
import hashlib
import argparse

class FileDeleter:
    def __init__(self, json_file):
        self.json_file = json_file
        try:
            with open(json_file, 'r') as f:
                self.delete_list = json.load(f)
        except FileNotFoundError:
            self.delete_list = []

    def get_file_info(self, filepath):
        size = os.path.getsize(filepath)
        with open(filepath, 'rb') as f:
            data = f.read()
            checksum = hashlib.sha256(data).hexdigest()
        return {'name': os.path.basename(filepath), 'size': size, 'checksum': checksum}

    def add_file_to_delete_list(self, filepath):
        file_info = self.get_file_info(filepath)
        if file_info not in self.delete_list:  # Check if file_info already exists in delete_list
            self.delete_list.append(file_info)

    def add_folder_to_delete_list(self, folderpath):
        folderpath = os.path.abspath(folderpath)  # Convert the folder path to absolute path
        for root, _, files in os.walk(folderpath):  # Remove the unused "dirs" variable
            for file in files:
                filepath = os.path.join(root, file)
                file_info = self.get_file_info(filepath)
                if file_info not in self.delete_list:  # Check if file_info already exists in delete_list
                    self.delete_list.append(file_info)

    def save_delete_list(self):
        with open(self.json_file, 'w') as f:
            json.dump(self.delete_list, f, indent=4)

    def delete_files(self, folderpath):
        files_to_delete = []
        for root, dirs, files in os.walk(folderpath):
            for file in files:
                filepath = os.path.join(root, file)
                file_info = self.get_file_info(filepath)
                for f in self.delete_list:
                    if f['name'] == file_info['name']:
                        if f['size'] == file_info['size']:
                            if f['checksum'] == file_info['checksum']:
                                files_to_delete.append(filepath)

        print(f"We found {len(files_to_delete)} files that should be deleted according to the provided json list.")
        confirm = input("Are you sure you want to continue? y/n: ")
        if confirm.lower() == 'y':
            for filepath in files_to_delete:
                print(f"Deleting \t{os.path.basename(filepath)} \tfrom \t{os.path.dirname(filepath)}")
                os.remove(filepath)
       
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Manage and delete files.')
    parser.add_argument('-a', '--add', help='Add a file to the delete list.')
    parser.add_argument('-d', '--addFolder', help='Add all files in a folder to the delete list.')
    parser.add_argument('-r', '--remove', help='Delete all files in a folder that are in the delete list.')
    args = parser.parse_args()

    deleter = FileDeleter("delete_list.json")

    if args.add:
        deleter.add_file_to_delete_list(args.add)
    if args.addFolder:
        deleter.add_folder_to_delete_list(args.addFolder)
    if args.remove:
        folderpath = os.path.abspath(args.remove)
        deleter.delete_files(folderpath)

    deleter.save_delete_list()