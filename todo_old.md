TODO List: Repo Audit, Edge Cases, and Improvements

This document lists findings from the repository audit, covering edge cases, potential bugs, design inefficiencies, and recommended improvements for the bitrot checking and garbage collection utilities.

================================================================================
1. Edge Cases & Potential Bugs
================================================================================

- [ ] AttributeError on Unitialized Lists in bitRotChecker.py
  - Bug: `self.skip_files`, `self.skip_extensions`, and `self.extensions_of_interest` are only initialized inside `read_json()`. If `create_dict()` is called without first running `read_json()`, or if `read_json()` fails to find the files, accessing these attributes will raise an `AttributeError`.
  - Fix: Initialize these variables as empty lists in `FileScanner.__init__`.

- [ ] Modifying List During Iteration in cleanup_json() (bitRotChecker.py)
  - Bug: At line 327, `cleanup_json()` iterates over a list (`tempDict[checksum]`) and modifies that same list by calling `remove(file)`. This causes Python to skip elements or behave unexpectedly.
  - Fix: Iterate over a copy of the list (e.g., `list(self.restructured_dict[checksum])` or using list comprehension) to perform deletions safely.

- [ ] Invalid Physical Drive Logic (bitRotChecker.py)
  - Bug: `get_physical_drive(filepath)` returns `os.path.dirname(filepath)` (the parent directory path) instead of the actual drive letter or mount point. Consequently, files in different folders on the same physical drive (e.g., `C:\FolderA` and `C:\FolderB`) are incorrectly treated as being on different physical drives. (Note: as a work around, I started storing everything in 'manual', 'manuam', manuan'.. folder. idea is, by checking the folder name, i'll be able to identify different storage media.)
  - Fix: On Windows, parse the drive letters (e.g., `os.path.splitdrive(filepath)[0]`). On Unix, parse the mount point.

- [ ] Out of Memory Error on Large Files in garbageFileCollector.py
  - Bug: `get_file_info()` reads the entire file into memory at once: `data = f.read()`. If the file is very large (e.g., video files, database dumps), this will trigger an `OutOfMemoryError`.
  - Fix: Compute the hash incrementally in chunks (e.g., 4096 bytes or 64KB) similar to how it is done in `bitRotChecker.py`.

- [ ] Windows Incompatibility for Unix Shell Commands (scripts/)
  - Bug: `checkBitRot.py`, `freeze.py`, and `writeHash.py` call command-line tools like `md5sum` and `freeze.sh` via `subprocess.Popen`. These external commands are not standard on Windows and will throw `FileNotFoundError`.
  - Fix: Implement fallback md5 computation using Python's native `hashlib` library if the CLI utilities are not found, or rewrite the commands using pure Python.

- [ ] Over-restrictive File Filter Logic in scan_dir() (bitRotChecker.py)
  - Bug: `scan_dir()` skips files with more than one dot (e.g., `file.tar.gz`, `v1.0.data`), files without dots (no extension), and extensions longer than 4 characters (e.g., `.ipynb`, `.config`, `.jpeg`).
  - Fix: Allow customizable extensions and use standard filename matching libraries like `fnmatch` or robust path split functions instead of arbitrary dot count rules.

================================================================================
2. Codebase Improvements & Optimization
================================================================================

- [ ] Eliminate Blocking Console Inputs in Automated Scans
  - Improvement: The `scan_dir()` function prompts the user via `input()` when a new file extension is discovered. This blocks execution and prevents the script from running in non-interactive environments (cron, automation scripts, Docker, etc.).
  - Fix: Provide command-line arguments to specify allowed extensions or auto-skip unmapped ones instead of requesting interactive console input.

- [ ] Optimize File Scanning and Hashing in garbageFileCollector.py
  - Improvement: `cleanup_folder()` currently calculates the full SHA-256 hash of *every* file in the directory to check if it's on the blacklist. For large directories, this requires excessive disk I/O.
  - Fix: Implement multi-stage filtering. Check filenames and file sizes first, and only compute checksums if the filename and size match an entry in the delete list.

- [ ] Path Normalization across Different OS Platforms
  - Improvement: Paths are not consistently normalized, which can result in duplicate entries due to differing casing (e.g., Windows drive letters `C:` vs `c:`), path separators (`/` vs `\`), and symlinks.
  - Fix: Consistently apply `os.path.normpath(os.path.casefold(abspath))` to filepaths before indexing them in the JSON registry.

- [ ] Missing Error/Exception Handling for File Operations
  - Improvement: File reads and permission access are not protected by `try-except` blocks. If a file is locked by another process or lacks permission, the entire script crashes.
  - Fix: Wrap disk reads and checksum calculations in `try-except OSError` blocks and log failures gracefully.

- [ ] Remove Dead and Duplicate Code
  - Improvement: In `bitRotChecker.py`, lines 353-354 instantiate `scanner` with the hardcoded `"target"` string, which is immediately overwritten by line 357. There are also duplicate `exit(0)` calls at the end of the script.
  - Fix: Clean up and refactor the `__main__` entry point.

- [ ] Revise README.md

- [ ] Everytime I come back to this directory, I keep forgeting how to actaully run these scripts. I don't know if it is the way the scripts are organized or the readme file. 

- [ ] Add docstring on every module, class and functions. Help the future me.


================================================================================
3. Feature wish list
================================================================================

- [ ] currently, the script can identify if there are more than or less than 2 copies of a data. But it cannot assist the user to delete the duplicate data or to copy the data at risk.
- [ ] currently, the JSON file filelist.json stores all the filenames and their location. but sometimes I need to find a specific data. such as, I'll take a photo of a birth certificate and store it in the photos directory. but the filename will be something like 20260101.jpg. I wish filelist.json would also hold a small description of the file. I could also be a new json file. maybe I could us LM studio, run a local server and use a local model as a one shot classifier?
- [ ] If I end up using LM studio or similar local AI, there should be a config file pointing to the LLM API. 
- [ ] Related to wish above, sometimes you need a little help to organize photos. like from one single photo you cannot tell that photo is one of many taken in a birthday party. before I setup a photo manager / organizer in my NAS, I need a helper script to organize / group photos in a folder.
- [ ] Re-organize the repo as per PEP / convention.
- [ ] Enable UV. Make this repo run as uv modules. such as 'uv run checkBitRot --arg --arg2'
- [ ] Automaeted pytest. Right now we are manually running the script on a test folder and checking output manually.

================================================================================
4. things to validate
================================================================================

- [ ] Are we using hardware accelerated hashing functions? Most CPU now a days have hash hardware. better to use that. even if that means we cannot keep using the same hashing algo, that is fine. I really need this script to be fast. and efficient.
