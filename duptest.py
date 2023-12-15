'''
Python script to
1. Scan a directory recursively.
2. list the filenames
3. list the file sizes
4. list the file checksums
5. list the file paths
6. store them in a dictionary'''

import os
import hashlib
import json
import sys
import argparse

class FileScanner:
    def __init__(self, path):
        self.path = path
        self.file_list = []
        self.file_dict = {}
        self.restructured_dict = {}
        self.unique_files = []
        self.duplicate_files = []

    def scan_dir(self):
        print("Scanning directory: " + self.path)
        for root, dirs, files in os.walk(self.path):
            for file in files:
                self.file_list.append(os.path.join(root, file))

    def checksum(self, file):
        sha256_hash = hashlib.sha256()
        with open(file, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()

    def create_dict(self):
        for file in self.file_list:
            self.file_dict[file] = {}
            self.file_dict[file]['size'] = os.path.getsize(file)
            self.file_dict[file]['checksum'] = self.checksum(file)
            self.file_dict[file]['path'] = file

    def write_json(self, json_file):
        with open(json_file, 'w') as f:
            json.dump(self.restructured_dict, f, indent=4)

    def read_json(self, json_file):
        with open(json_file, 'r') as f:
            self.file_dict = json.load(f)

    def restructure_dict(self):
        for file in self.file_dict:
            checksum = self.file_dict[file]['checksum']
            if checksum in self.restructured_dict:
                self.restructured_dict[checksum]['details'].append((self.file_dict[file]['path'], self.file_dict[file]['size']))
            else:
                self.restructured_dict[checksum] = {
                    'details': [(self.file_dict[file]['path'], self.file_dict[file]['size'])]
                }

    def find_unique_files(self):
            for checksum in self.restructured_dict:
                if len(self.restructured_dict[checksum]['details']) == 1:
                    self.unique_files.append(self.restructured_dict[checksum]['details'][0])
       

    def find_duplicate_files(self):
        for checksum in self.restructured_dict:
            if len(self.restructured_dict[checksum]['details']) > 2:
                self.duplicate_files.append(self.restructured_dict[checksum]['details'])

    
   
    
    def display_unique_files(self):
         for itemss in self.unique_files:
            print(itemss[0], end= "\t")
            print(itemss[1])
    
   
    def display_duplicate_files(self):
        print("Duplicate files:")
        for files in self.duplicate_files:
            print(f"File: {files[0][0]}")
            for file in files:
                print(f"\tPath: {file[0]}", end= " ")
                print(f"\tSize: {file[1]} bytes")
            print("\n")

if __name__ == "__main__":
    # Parse the command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--path', help="Path to the directory to be scanned")
    args = parser.parse_args()

    # show args help if no arguments are passed
    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(1)

    # Create a FileScanner object
    scanner = FileScanner(args.path)

    # Scan the directory recursively
    scanner.scan_dir()

    # Create a dictionary of files, file sizes, checksums and paths
    scanner.create_dict()

    # Restructure the dictionary
    scanner.restructure_dict()

    # Find the files that appear only once
    scanner.find_unique_files()

    # Find the files that appear more than twice
    scanner.find_duplicate_files()

    # Write the dictionary to a json file
    scanner.write_json("result.json")

    # Print the results
    scanner.display_duplicate_files()
    print("\n")
    scanner.display_unique_files()
