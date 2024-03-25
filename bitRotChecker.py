'''
Python script to
1. Scan a directory recursively.
2. list the filenames
3. list the file sizes
4. list the file checksums
5. list the file paths
6. store them in a dictionary

Goal of this script:
Find the files which have more that 2 copies. >> So you can save disk space.
Find the files which have only 1 copy. >> So you can duplicate them for redundancy.

Since I have multiple drives and multiple PC, this script is to make sure 
I have all the data where I want it to be. 
'''

# %%
import os
import hashlib
import json
import sys
import argparse

# %%
class FileScanner:
    def __init__(self, path, debugFlag=False, verboseFlag=False):
        self.path = path
        
        self.restructured_dict = {}
        # { 'checksum': [
        #      {'fullpath': str path of the file, 
        #       'size': int size of the file}]

        self.debugMode = debugFlag
        self.verboseMode = verboseFlag

    def scan_dir(self):
        '''
        You give it a directory,
        it will return you a generator object.
        Filenames. expect for the file names or extenssion you told it to skip.'''

        print("Scanning directory: " + self.path)
        for root, dirs, files in os.walk(self.path):
            for item in files:
                if os.path.isdir(item):
                    if self.verboseMode:
                        print("Directory. Skipping: " + item)
                    continue

                if "." not in item:
                    if self.verboseMode:
                        print("No dot. Skipping: " + item)
                    continue

                if item in self.skip_files:
                    if self.verboseMode:
                        print("Skipping file: " + item)
                    continue
                
                if os.path.basename(item).split('.')[-1] in self.skip_extensions:
                    if self.verboseMode:
                        print("Skipping file: " + item)
                    continue

                if os.path.basename(item).split('.')[-1] not in self.extensions_of_interest:
                    userInput = input("Do you want add " + item + " to extensions_of_interest? (y/n)? ")
                    if userInput == 'y':
                        self.extensions_of_interest.append(os.path.basename(item).split('.')[-1])
                    else:
                        self.skip_extensions.append(os.path.basename(item).split('.')[-1])
                        if self.verboseMode:
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
        ''' It'll read the target directory. 
        It'll create a dictionary of the files in the directory.'''

        for filepath in self.scan_dir():
            checksum = self.checksum(filepath)
            if checksum in self.restructured_dict:
                isAlreadyThere = False
                for individual_dict in self.restructured_dict[checksum]:
                    if individual_dict['fullpath'] == filepath:
                        if self.verboseMode:
                            print("Skipping file: " + filepath)
                        isAlreadyThere = True
                if not isAlreadyThere:
                    self.restructured_dict.get(checksum).append({'fullpath': filepath, 'size': os.path.getsize(filepath)})
            else:
                self.restructured_dict[checksum] = [{'fullpath': filepath, 'size': os.path.getsize(filepath)}]

    def write_json(self, json_filelist, json_extlist):
        with open(json_extlist, 'w') as f:
            json.dump({"skip_files": self.skip_files, "skip_extensions": self.skip_extensions, "extensions_of_interest": self.extensions_of_interest}, f, indent=4)
        
        with open(json_filelist, 'w') as f:
            json.dump(self.restructured_dict, f, indent=4)

    def read_json(self, json_filelist, json_extlist):
        try:
            with open(json_extlist, 'r') as f:
                temp_dict = json.load(f)
            self.skip_files = temp_dict.get("skip_files", [])
            self.skip_extensions = temp_dict.get("skip_extensions", [])
            self.extensions_of_interest = temp_dict.get("extensions_of_interest", [])
        except FileNotFoundError:
            print("First run it must be.")
            self.skip_files = []
            self.skip_extensions = []
            self.extensions_of_interest = []
        
        try:
            with open(json_filelist, 'r') as f:
                self.restructured_dict = json.load(f)
        except FileNotFoundError:
            print("First run it must be.")
            self.restructured_dict = {}
    
    def isItRotten(self, filepath):
        subDict_filename = self.create_dosier(filepath)
        filtered_subDict = {}
        desired_size = os.path.getsize(filepath)
        if self.verboseMode and self.debugMode:
            print(json.dumps(subDict_filename, indent=4))
            print("Desired size: " + str(desired_size))
        for checksum in subDict_filename:
            for file in subDict_filename[checksum]: # file is a dictionary
                if file['size'] == desired_size:
                    filtered_subDict[checksum] = [file]
        if self.verboseMode and self.debugMode:
            print("After filtering by size")
            print(json.dumps(filtered_subDict, indent=4))
        for key in list(filtered_subDict.keys()):
            if not filtered_subDict[key]:
                del filtered_subDict[key]
        if self.verboseMode and self.debugMode:
            print("After removing empty lists")
            print(json.dumps(filtered_subDict, indent=4))

        if len(filtered_subDict) > 1:
            if self.verboseMode and self.debugMode:
                print("Possible bitrot")
                print(json.dumps(filtered_subDict, indent=4))
            return True, filtered_subDict
        return False, filtered_subDict

    # def restructure_dict(self):
    #     for file in self.file_dict:
    #         checksum = self.file_dict[file]['checksum']
    #         if checksum in self.restructured_dict:
    #             if self.restructured_dict.get(checksum)
    #                 self.restructured_dict.get(checksum).append({'fullpath': self.file_dict[file]['path'], 'size': self.file_dict[file]['size']})
    #         else:
    #             self.restructured_dict[checksum] = [{'fullpath': self.file_dict[file]['path'], 'size': self.file_dict[file]['size']}]
    #         print(self.restructured_dict)

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
    
    def create_dosier(self, filepath):
        '''
        You give it a path.
        It will give you a sub-dictionary of the restructured_dict
        with details of all the files with same name. 
        Regardless of the location or size or checksum.'''
        filename = os.path.basename(filepath)
        subDict_filename = {}
        for checksum in self.restructured_dict.keys():
            for file in self.restructured_dict[checksum]:
                # if file is not a dictionary, skip it
                if type(file) != dict:
                    continue
                thisFilename = os.path.basename(file['fullpath'])
                if thisFilename == filename:
                    if checksum in subDict_filename:
                        subDict_filename[checksum].append(file)
                    else:
                        subDict_filename[checksum] = [file]
        return subDict_filename

    def display_unique_files(self):
        print("\nUnique files:")
        for checksumValue in self.find_unique_files():
            print(self.restructured_dict[checksumValue][0]['fullpath'])
    
    def display_duplicate_files(self):
        print("\nDuplicate files:")
        for checksumValue in self.find_duplicate_files():
            print("--")
            for file in self.restructured_dict[checksumValue]:
                try:
                    print(checksumValue, end= " ")
                    print(file['size'], end= "\t")
                    print(file['fullpath'])
                except TypeError:
                    continue
            print("--")

# %%
if __name__ == "__main__":
    # Parse the command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--path', help="Path to the directory to be scanned", required=True)
    parser.add_argument('-u', '--unique', help="Display unique files", action="store_true")
    parser.add_argument('-c', '--duplicate', help="Display duplicate files", action="store_true")
    parser.add_argument('-b', '--bitrot', help="Display bitrot files", action="store_true")
    parser.add_argument('-d', '--debugMode', help="Enable debug mode. Logs more details.", action="store_true")
    parser.add_argument('-v', '--verboseMode', help="Enable verbose mode. Prints more details.", action="store_true")
    parser.add_argument('-j', '--updateJson', help="Update the json file", action="store_true")

    args = parser.parse_args()

    # show args help if no arguments are passed
    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(1)

    # %%
    scanner = FileScanner("target")

    # %%
    # Create a FileScanner object
    scanner = FileScanner(args.path, debugFlag=args.debugMode, verboseFlag=args.verboseMode)
    # %%
    scanner.read_json("filelist.json") # It doesn't happen auto. so don't forget it. 
    # %%
    # Create a dictionary of files, file sizes, checksums and paths
    scanner.create_dict() # Execute after read_json(). Provided you have a json file from past run. 

    # %%
    # Write the dictionary to a json file
    if args.updateJson:
        scanner.write_json("filelist.json")

    # %%
    # Print the results
    if args.unique:
        scanner.display_unique_files()
    if args.duplicate:
        scanner.display_duplicate_files()

    # Bitrot
    if args.bitrot:
        # %%
        for filepath in scanner.scan_dir():
            resultBool, resultDict = scanner.isItRotten(filepath)
            if resultBool:
                print("\nPossible bitrot")
                for checksum in resultDict.keys():
                    for file in resultDict[checksum]:
                        print(checksum, end= " ")
                        print(file['size'], end= "\t")
                        print(file['fullpath'])
    # %%
    exit(0)

# %%
path = "target"
with open("filelist.json", 'r') as f:
    restructured_dict = json.load(f)
# %%
filepath = "C:\\Users\\MaisunIbnMonowar\\Downloads\\gitrepo\\bitrot\\target\\dir1\\myfile.txt"
filename = os.path.basename(filepath)
# %%
filepath = "C:\\Users\\MaisunIbnMonowar\\Downloads\\gitrepo\\bitrot\\target\\dir1\\ex\\test.txt"
filename = os.path.basename(filepath)
# %%

# def find_possible_bitrot(restructured_dict):
# Find the exact path in our restructured_dict
subDict_fullpath = {}
for checksum in restructured_dict.keys():
    for file in restructured_dict[checksum]:
        # if file is not a dictionary, skip it
        if type(file) != dict:
            continue
        if file['fullpath'] == filepath:
            # print("Found the file")
            # print(file)
            # print(checksum)
            if checksum in subDict_fullpath:
                subDict_fullpath[checksum].append(file)
            else:
                subDict_fullpath[checksum] = [file]
subDict_filename = {}
for checksum in restructured_dict:
    for file in restructured_dict[checksum]:
        # if file is not a dictionary, skip it
        if type(file) != dict:
            continue
        thisFilename = os.path.basename(file['fullpath'])
        if thisFilename == filename:
            # print("Found the file")
            # print(file)
            # print(checksum)
            if checksum in subDict_filename:
                subDict_filename[checksum].append(file)
            else:
                subDict_filename[checksum] = [file]
print(json.dumps(subDict_filename, indent=4))         
# %%
# Now we have to determine if filepath is rotten or not
# we have subDict_filename 
# So we need to filter subDict_filename. Only same filesize remains
desired_size = os.path.getsize(filepath)
for checksum in subDict_filename:
    for file in subDict_filename[checksum]: # file is a dictionary
        if file['size'] == desired_size:
            print("keep this file")
        else:
            print("delete this file")
            subDict_filename[checksum].remove(file)
print(json.dumps(subDict_filename, indent=4))            
            
            
# %%
# remove key value pair from dictionary where value is empty list
for key in list(subDict_filename.keys()):
    if not subDict_filename[key]:
        del subDict_filename[key]
print(json.dumps(subDict_filename, indent=4))
# %%
if len(subDict_filename) > 1:
    print("Possible bitrot")
    print(json.dumps(subDict_filename, indent=4))
# %%
