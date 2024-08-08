# Background

BIT ROT
Although bit rot is not so common nowadays, it doesn't hurt to create backup copies of your super important files. Your image files maybe be not so vulnerable to single bit filp, but how about your private keys? How do you detect your private keys suffered a data corruption?

FILE MANAGEMENT
Ideally, you should follow a 3 2 1 backup policy. Maybe 2 NAS syncing overnight, with weekly backup to the offsite location. But in reality who has that money and time. So I use this tool to assist me. Scanning for duplicate files. Scanning for files that are only single copy. 

# Goal

Repackage super important file so that you can recover them from partial data corruption. 

Make sure no important file has only single copy. 

Make sure you don't have more that 3 copies of the same file in your collection. 

Make sure that you don't have more than 2 copies of the same file on a same drive. 

# Setup

The whole thing relies on Mr. Tsiodras's implementation of rsbep packaging. The idea is, the file should be able to self recover from few data corruption. You can read more here, https://www.thanassis.space/rsbep.html. 

First install Mr. Tsiodras's custom version of rsbep, 
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

## Recover the file
To recover the file `foo.bar`, you must have `foo.bar.frozen`. 
Run 
```
melt.sh foo.bar.frozen > foo_recovered.bar
```

## Scan and update file hash

## Add files to delete list

`python3 garbageFileCollector.py --add file.foo` marks only the file as garbage.

`python3 garbageFileCollector.py --addFolder /path/to/folder` marks whole folder as garbage. 



## Assited duplicate deleter

There maybe a case, where you know you successfully backedup files. but this folder has duplicate files. 
use `python3 bitRotChecker.py --path /to/target/folder --deleteDuplicate --updateJson`

ALWAYS USE UPDATEJSON ARG. 

It will go through the folder. check against the json file, and if there is any file in the folder
which is a duplicate of file already backup, it will be deleted. 

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
