'''
Python script to
1. Scan a directory recursively.
2. list the filenames
3. list the file sizes
4. list the file checksums
5. list the file paths
6. store them in a dictionary'''

# %%
import os
import hashlib
import json
import sys
import argparse

# %%
class FileScanner:
    def __init__(self, path):
        self.path = path
        
        self.restructured_dict = {}
        # { 'checksum': [
        #      {'fullpath': str path of the file, 
        #       'size': int size of the file}]

        self.skip_files = ['DS_Store', 'Thumbs.db', 'desktop.ini']
        self.skip_extensions = ['lnk', 'url']

    def scan_dir(self):
        print("Scanning directory: " + self.path)
        for root, dirs, files in os.walk(self.path):
            for item in files:
                if item in self.skip_files:
                    print("Skipping file: " + item)
                    continue
                
                if os.path.basename(item).split('.')[-1] in self.skip_extensions:
                    print("Skipping file: " + item)
                    continue
                
                yield os.path.abspath(os.path.join(root, item))

    def checksum(self, file):
        sha256_hash = hashlib.sha256()
        with open(file, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()

    def create_dict(self):
        for filepath in self.scan_dir():
            checksum = self.checksum(filepath)
            if checksum in self.restructured_dict:
                self.restructured_dict.get(checksum).append({'fullpath': filepath, 'size': os.path.getsize(filepath)})
            else:
                self.restructured_dict[checksum] = [{'fullpath': filepath, 'size': os.path.getsize(filepath)}]

    def write_json(self, json_file):
        with open(json_file, 'w') as f:
            json.dump(self.restructured_dict, f, indent=4)

    def read_json(self, json_file):
        with open(json_file, 'r') as f:
            self.restructured_dict = json.load(f)

    def restructure_dict(self):
        for file in self.file_dict:
            checksum = self.file_dict[file]['checksum']
            if checksum in self.restructured_dict:
                self.restructured_dict.get(checksum).append({'fullpath': self.file_dict[file]['path'], 'size': self.file_dict[file]['size']})
            else:
                self.restructured_dict[checksum] = [{'fullpath': self.file_dict[file]['path'], 'size': self.file_dict[file]['size']}]
            print(self.restructured_dict)

    def find_unique_files(self):
            for checksum in self.restructured_dict:
                if len(self.restructured_dict[checksum]) == 1:
                    yield checksum
       
    def find_duplicate_files(self):
        '''
        Defination of duplicate files:
        more than 2 files with same checksum'''

        for checksum in self.restructured_dict:
            if len(self.restructured_dict[checksum]) > 2:
                yield checksum

    def display_unique_files(self):
        print("Unique files:")
        for checksumValue in self.find_unique_files():
            print(self.restructured_dict[checksumValue][0]['fullpath'])
    
    def display_duplicate_files(self):
        print("Duplicate files:")
        for checksumValue in self.find_duplicate_files():
            print("--")
            for file in self.restructured_dict[checksumValue]:
                print(file['fullpath'])
            print("--")

# %%
if __name__ == "__main__":
    # Parse the command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--path', help="Path to the directory to be scanned")
    args = parser.parse_args()

    # show args help if no arguments are passed
    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(1)

    # %%
    scanner = FileScanner("target")
    # %%
    scanner = FileScanner("target2")
    # %%
    # Create a FileScanner object
    scanner = FileScanner(args.path)
    # %%
    scanner.read_json("filelist.json")
    # %%
    # Create a dictionary of files, file sizes, checksums and paths
    scanner.create_dict()

    # %%
    # Write the dictionary to a json file
    scanner.write_json("filelist.json")

    # %%
    # Print the results
    scanner.display_duplicate_files()
    print("\n")
    scanner.display_unique_files()

# %%
