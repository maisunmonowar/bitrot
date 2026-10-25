# Background

BIT ROT
Although bit rot is not so common nowadays, it doesn't hurt to create backup copies of your super important files. Your image files maybe be not so vulnerable to single bit filp, but how about your private keys? How do you detect your private keys suffered a data corruption?

FILE MANAGEMENT
Ideally, you should follow a 3 2 1 backup policy. Maybe 2 NAS syncing overnight, with weekly backup to the offsite location. But in reality who has that money and time. So I use this tool to assist me. Scanning for duplicate files. Scanning for files that are only single copy. 

# Goal

Repackage super important file so that you can recover them from partial data corruption. 

Make sure no important file has only single copy.

Keep no more than three copies of a file in total and no more than two copies
on any one mounted volume.

## Duplicate-count policy

The duplicate report flags a checksum when it has more than three copies total
or more than two copies on any one mounted volume. Three copies split 2+1
across two volumes are allowed. Three copies on one volume are flagged, as are
four copies split 2+2 across two volumes. Both duplicate reporting and the
assisted duplicate-cleanup flow use this same rule.

Help organize, index your data.

Text / JSON heavy output as we want to use this scripts across platform and decades.

# Setup

The recovery format began with Mr. Tsiodras's implementation of rsbep packaging.
The project keeps its C format and engine while providing a Python CLI for
cross-platform invocation.

## Recovery tools

`rsbep_cli.py` provides a cross-platform Python command-line interface around the
original C encoder. The GitHub Actions workflow builds native `rsbep` executables
for Windows, macOS, and Linux; download the artifact for your platform and place
the executable in the repository's `bin/` directory. Alternatively, build locally
with a C compiler after initializing the submodule and applying the safety patch:

```
git submodule update --init rsbep-backup
git apply patches/rsbep-safety.patch
mkdir bin
cc -O2 -std=gnu99 -o bin/rsbep rsbep-backup/src/rsbep.c rsbep-backup/src/rs.c
```

On Windows, use a MinGW-w64 toolchain such as MSYS2 and name the output
`bin/rsbep.exe`.

Encode and recover a file without Docker:

```
python rsbep_cli.py freeze important.file important.file.frozen
python rsbep_cli.py melt important.file.frozen important.file.recovered
```

The wrapper checks the C program's exit status, rejects truncated streams, and
only replaces an existing destination after a successful operation. The C code
remains the recovery engine, preserving its format and performance. Reed-Solomon
cannot guarantee detection of every possible miscorrection; keep independent
backups.

### Legacy C scripts

The original scripts remain under `rsbep-backup/contrib/`. To build and use them
directly, install Mr. Tsiodras's custom version of rsbep:
Download the source from, https://www.thanassis.space/rsbep-0.1.0-ttsiodras.tar.bz2
Extract the folder. 
Then install by usual 
```
./configure
make 
install
```
on successfull install, 
```
maisun@ubuntu:~/Desktop$ freeze.sh

Usage: /usr/local/bin/freeze.sh filename (... will output to stdout)
```

Then copy the 3 files, 
freeze.py, writeHash.py & checkBitRot.py

# Some common use cases

## Repackage your file
First run, 
`python3 freeze.py`

Then, `python3 writeHash.py`

This will calculate the md5 hash of all the files in the working directory and save them in the working directory. Also creates `foo.bar.frozen` from `foo.bar`. `foo.bar.frozen` is what you need incase of data corruption. 


## Check for file corruption

`python3 checkBitRot.py --path /path/to/target --updateJson`

if you don't use --updateJson, additional calculation will happen in RAM and won't be saved. 

If everything is ok, the terminal will be blank. If anyfile has been changed/corrupted since recording the hash, it'll show up. 

The `melt.sh` script can still be used in Docker.

## Recover the file with the legacy C script
To recover the file `foo.bar`, you must have `foo.bar.frozen`.
Run 
```
melt.sh foo.bar.frozen > foo_recovered.bar
```

## Scan and update file hash

## Add files to delete list

`python3 garbageFileCollector.py --add file.foo` marks only that absolute path
as garbage. Identical files at other paths are not affected.

`python3 garbageFileCollector.py --addFolder /path/to/folder` marks each file
under that folder by its absolute path.

Older garbage-list entries without a saved path are ignored during cleanup
because they cannot safely identify a specific file.



## Assited duplicate deleter

There maybe a case, where you know you successfully backedup files. but this folder has duplicate files. 
use `python3 bitRotChecker.py --path /to/target/folder --deleteDuplicate --updateJson`

This command is a dry run: it shows the exact paths planned for deletion and the
copy retained for each checksum. Review the plan, then add `--confirmDelete` to
execute it. Files outside the requested scan directory are never deleted, and
cleanup aborts if it cannot verify a matching copy to retain.

ALWAYS USE UPDATEJSON ARG. 

It will go through the folder and compare its files with the JSON registry.
Only paths in the requested scan directory can be included in the deletion plan.

Example, maybe you have a folder in the pendrive. Likely be be copied from backup drive. 

## Delete garbage files.

`python3 garbageFileCollector.py --cleanup /path/to/folder` Will delte only the 'garbage'

`python3 garbageFileCollector.py --remove /path/to/folder` first add to the list. then delte everything. 


Note: Garbage files are like blacklist files. It won't care if there a backup. If the files is in the list, it will be deleted. 


# Limitation

For some reason, png files cannot be recovered. In somecases, I see files with spaces in their filename does do so well. 

# Disclaimer
I am not liable for any data loss you might have on your computer. This script doesn't come with any guarantee. 


# Docker build 
docker build -t test . 
docker run --rm -it --mount type=bind,source="$(pwd)"\target,target=/target test
