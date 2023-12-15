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

# Function to scan a directory recursively and return a list of files
def scan_dir(path):
    file_list = []
    print("Scanning directory: " + path)
    for root, dirs, files in os.walk(path):
        for file in files:
            file_list.append(os.path.join(root, file))
    return file_list

# Function to calculate the checksum of a file
def checksum(file):
    sha256_hash = hashlib.sha256()
    with open(file,"rb") as f:
        for byte_block in iter(lambda: f.read(4096),b""):
            sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()
    
# Function to create a dictionary of files, file sizes, checksums and paths
def create_dict(file_list):
    file_dict = {}
    for file in file_list:
        file_dict[file] = {}
        file_dict[file]['size'] = os.path.getsize(file)
        file_dict[file]['checksum'] = checksum(file)
        file_dict[file]['path'] = file
    return file_dict

# Function to write the dictionary to a json file
def write_json(file_dict, json_file):
    with open(json_file, 'w') as f:
        json.dump(file_dict, f, indent=4)
    return

# Function to read the json file and return the dictionary
def read_json(json_file):
    with open(json_file, 'r') as f:
        file_dict = json.load(f)
    return file_dict
# restructure the dictionary to have the checksum as the key
def restructure_dict(file_dict):
    restructured_dict = {}
    for file in file_dict:
        checksum = file_dict[file]['checksum']
        if checksum in restructured_dict:
            restructured_dict[checksum]['details'].append((file_dict[file]['path'], file_dict[file]['size']))
        else:
            restructured_dict[checksum] = {
                'details': [(file_dict[file]['path'], file_dict[file]['size'])]
            }
    return restructured_dict

# Function to find files that appear only once
def find_unique_files(restructured_dict):
    unique_files = []
    for checksum in restructured_dict:
        if len(restructured_dict[checksum]['details']) == 1:
            unique_files.append(restructured_dict[checksum]['details'][0])
    return unique_files

# Function to find the files that appear more that 2 times
def find_duplicate_files(restructured_dict):
    duplicate_files = []
    for checksum in restructured_dict:
        if len(restructured_dict[checksum]['details']) > 2:
            duplicate_files.append(restructured_dict[checksum]['details'])
    return duplicate_files

# Main function
if __name__ == "__main__":
    # Parse the command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--path', help="Path to the directory to be scanned")
    args = parser.parse_args()

    # show args help if no arguments are passed
    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(1)
    
    # Scan the directory recursively
    file_list = scan_dir(args.path)
    
    # Create a dictionary of files, file sizes, checksums and paths
    file_dict = create_dict(file_list)
    
    # restructure:
    restructured_dict = restructure_dict(file_dict)

    # Find the files that appear only once
    unique_files = find_unique_files(restructured_dict)
    print("Unique files: ")
    print(unique_files)

    # Find the files that appear more than twice
    duplicate_files = find_duplicate_files(restructured_dict)
    print("Duplicate files: ")
    print(duplicate_files)

    # Write the dictionary to a json file
    write_json(restructured_dict, "result.json")

    # Print the dictionary
    print(restructured_dict)