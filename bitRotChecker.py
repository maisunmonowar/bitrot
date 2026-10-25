'''
Python script to
1. Scan a directory recursively.
2. list the filenames
3. list the file sizes
4. list the file checksums
5. list the file paths
6. store them in a dictionary

Goal of this script:
Find files that exceed the configured copy limits, so you can save disk space.
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

class filehash_storage:
    def __init__(self, path):
        self.path = os.path.abspath(path)
        self.hash_dict = {}
        # { 'file_basename': checksum}
    
    def savefile(self):
        if self.hash_dict:
            with open(os.path.join(self.path, "filehash.json"), "w") as f:
                json.dump(self.hash_dict, f, indent=4)

# %%
class FileScanner:
    def __init__(self, path, debugFlag=False, verboseFlag=False):
        self.path = os.path.abspath(path)
        
        self.restructured_dict = {}
        # { 'checksum': [
        #      {'fullpath': str path of the file, 
        #       'size': int size of the file}]

        self.newly_hashed_files = {}
        # {'c://path/to/dir': filehash_storage()}

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

                if len(item.split('.')) > 2:
                    if self.verboseMode:
                        print("More than one dot. Skipping: " + item)
                    continue

                if len(item.split('.')[-1]) > 4:
                    if self.verboseMode:
                        print("Extension too long. Skipping: " + item)
                    continue
                if item == "filehash.json":
                    # Read this file and update self.restructured_dict
                    filehash_path = os.path.join(root, item)
                    try:
                        with open(filehash_path, "r") as f:
                            hash_dict = json.load(f)
                        for filename, checksum in hash_dict.items():
                            abs_path = os.path.abspath(os.path.join(root, filename))
                            size = os.path.getsize(abs_path) if os.path.exists(abs_path) else None
                            if size is not None:
                                entry = {'fullpath': abs_path, 'size': size}
                                if checksum in self.restructured_dict:
                                    # Avoid duplicates
                                    if not any(e['fullpath'] == abs_path for e in self.restructured_dict[checksum]):
                                        self.restructured_dict[checksum].append(entry)
                                else:
                                    self.restructured_dict[checksum] = [entry]
                    except Exception as e:
                        if self.verboseMode:
                            print(f"Failed to process {filehash_path}: {e}")
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
        if self.verboseMode:
            print("Calculating checksum for: " + file)
        this_file_hash = self.calculate_checksum(file)
        this_file_dir = os.path.dirname(file)
        this_file_basename = os.path.basename(file)
        if this_file_dir in self.newly_hashed_files:
            self.newly_hashed_files[this_file_dir].hash_dict[this_file_basename] = this_file_hash
        else:
            self.newly_hashed_files[this_file_dir] = filehash_storage(this_file_dir)
            self.newly_hashed_files[this_file_dir].hash_dict[this_file_basename] = this_file_hash

        return this_file_hash

    @staticmethod
    def calculate_checksum(filepath):
        sha256_hash = hashlib.sha256()
        with open(filepath, "rb") as f:
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
        """Return checksums with more than three copies or over two per drive."""
        duplicate_files = []
        for checksum in self.restructured_dict:
            file_copies = self.restructured_dict[checksum]
            copies_per_drive = {}
            for file_copy in file_copies:
                drive = self.get_physical_drive(file_copy["fullpath"])
                copies_per_drive[drive] = copies_per_drive.get(drive, 0) + 1

            if len(file_copies) > 3 or any(count > 2 for count in copies_per_drive.values()):
                duplicate_files.append(checksum)

        return duplicate_files

    def get_physical_drive(self, filepath):
        '''
        Get the physical drive name from the file path.
        '''
        drive = os.path.dirname(filepath)
        return drive

    def build_duplicate_deletion_plan(self, duplicate_checksums):
        scan_root = os.path.realpath(self.path)
        deletion_plan = {}
        retained_files = {}

        for checksum in duplicate_checksums:
            verified_inside = []
            verified_outside = []
            seen_paths = set()

            for entry in self.restructured_dict.get(checksum, []):
                if not isinstance(entry, dict) or not entry.get("fullpath"):
                    raise ValueError(
                        f"Cannot safely determine copies for checksum {checksum}: "
                        "a registry entry has no file path."
                    )

                filepath = os.path.abspath(entry["fullpath"])
                realpath = os.path.realpath(filepath)
                normalized_path = os.path.normcase(realpath)
                if normalized_path in seen_paths:
                    continue
                seen_paths.add(normalized_path)

                if os.path.islink(filepath) or not os.path.isfile(filepath):
                    continue
                if self.calculate_checksum(filepath) != checksum:
                    continue

                try:
                    is_inside = os.path.commonpath([scan_root, realpath]) == scan_root
                except ValueError:
                    is_inside = False

                if is_inside:
                    verified_inside.append(filepath)
                else:
                    verified_outside.append(filepath)

            if not verified_inside and not verified_outside:
                raise ValueError(
                    f"Cannot safely delete checksum {checksum}: no existing copy "
                    "matches the recorded checksum."
                )

            if verified_outside:
                retained_files[checksum] = sorted(verified_outside)[0]
                deletion_plan[checksum] = sorted(verified_inside)
            else:
                verified_inside.sort()
                retained_files[checksum] = verified_inside[0]
                deletion_plan[checksum] = verified_inside[1:]

        return deletion_plan, retained_files

    def execute_duplicate_deletion_plan(self, deletion_plan, retained_files):
        scan_root = os.path.realpath(self.path)

        for checksum, retained_path in retained_files.items():
            if not os.path.isfile(retained_path) or os.path.islink(retained_path):
                raise ValueError(f"Retained copy is no longer available: {retained_path}")
            if self.calculate_checksum(retained_path) != checksum:
                raise ValueError(f"Retained copy changed after planning: {retained_path}")

            for filepath in deletion_plan.get(checksum, []):
                realpath = os.path.realpath(filepath)
                try:
                    is_inside = os.path.commonpath([scan_root, realpath]) == scan_root
                except ValueError:
                    is_inside = False
                if not is_inside:
                    raise ValueError(f"Refusing to delete a path outside the scan directory: {filepath}")
                if os.path.islink(filepath) or not os.path.isfile(filepath):
                    raise ValueError(f"Planned file is no longer available: {filepath}")
                if self.calculate_checksum(filepath) != checksum:
                    raise ValueError(f"Planned file changed after planning: {filepath}")

        for checksum, paths in deletion_plan.items():
            for filepath in paths:
                print(f"Deleting: {filepath} (checksum {checksum})")
                os.remove(filepath)

    
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

    def cleanup_json(self):
        # check self.restructured_dict. if the file no longer exists, remove it from the dictionary
        tempDict = self.restructured_dict
        for checksum in tempDict.keys():
            for file in tempDict[checksum]:
                if not os.path.exists(file['fullpath']):
                    self.restructured_dict[checksum].remove(file)

# %%
if __name__ == "__main__":
    # Parse the command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--path', help="Path to the directory to be scanned", required=True)
    parser.add_argument('-u', '--displayUnique', help="Display unique files", action="store_true")
    parser.add_argument('-c', '--displayDuplicate', help="Display duplicate files", action="store_true")
    parser.add_argument('-b', '--checkBitrot', help="Display bitrot files", action="store_true")
    parser.add_argument('-d', '--debugMode', help="Enable debug mode. Logs more details.", action="store_true")
    parser.add_argument('-v', '--verboseMode', help="Enable verbose mode. Prints more details.", action="store_true")
    parser.add_argument('-j', '--updateJson', help="Use it to store the progress to JSON file. Otherwise, all calculation in RAM.", action="store_true")
    parser.add_argument('-a', '--deleteDuplicate', help='Assisted duplicate cleanup. If you think your provide path is the duplicate folder, it will delete all the duplicate file.', action='store_true')
    parser.add_argument('--confirmDelete', help="Execute the deletion plan shown by --deleteDuplicate. Without this flag, cleanup is a dry run.", action="store_true")

    args = parser.parse_args()
    if args.confirmDelete and not args.deleteDuplicate:
        parser.error("--confirmDelete requires --deleteDuplicate")

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
    scanner.read_json("filelist.json", "extlist.json") # It doesn't happen auto. so don't forget it. 
    # %%
    # Create a dictionary of files, file sizes, checksums and paths
    scanner.create_dict() # Execute after read_json(). Provided you have a json file from past run. 
    # Create dictionary will create only for provided path. If you read_json() before, 
    # it will append to the existing dictionary.

    

    # %%
    # Print the results
    if args.displayUnique:
        # %%
        scanner.display_unique_files()
    if args.displayDuplicate:
        # %%
        scanner.display_duplicate_files()

    # Bitrot
    if args.checkBitrot:
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
    # Assisted cleanup. The default is a dry run; deletion requires explicit confirmation.
    if args.deleteDuplicate:
        print("Assisted cleanup")
        try:
            deletion_plan, retained_files = scanner.build_duplicate_deletion_plan(
                scanner.find_duplicate_files()
            )
            planned_count = sum(len(paths) for paths in deletion_plan.values())
            print(f"Planned deletions: {planned_count}")
            for checksum, paths in deletion_plan.items():
                print(f"Checksum {checksum}; keeping: {retained_files[checksum]}")
                for filepath in paths:
                    print(f"  Delete: {filepath}")
            if args.confirmDelete:
                scanner.execute_duplicate_deletion_plan(deletion_plan, retained_files)
            else:
                print("Dry run only. Re-run with --confirmDelete to execute this exact plan.")
        except (OSError, ValueError) as error:
            print(f"Duplicate cleanup aborted: {error}", file=sys.stderr)
            sys.exit(1)
    # Write the dictionary to a json file
    if args.updateJson:
        # %%
        scanner.cleanup_json()
        scanner.write_json("filelist.json", "extlist.json") 
        for dir_filehash in scanner.newly_hashed_files:
            scanner.newly_hashed_files[dir_filehash].savefile()
    # %%
    exit(0)
    # %%
    exit(0)
