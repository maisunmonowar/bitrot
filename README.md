# Background
Although bit rot is not so common nowadays, it doesn't hurt to create backup copies of your super important files. Your image files maybe be not so vulnerable to single bit filp, but how about your private keys? How do you detect your private keys suffered a data corruption?
# Goal
Repackage super important file so that you can recover them from partial data corruption. 

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


# Repackage your file
First run, 
`python3 freeze.py`

Then, `python3 writeHash.py`

This will calculate the md5 hash of all the files in the working directory and save them in the working directory. Also creates `foo.bar.frozen` from `foo.bar`. `foo.bar.frozen` is what you need incase of data corruption. 


# Check for file corruption
`python3 checkBitRot.py`

If everything is ok, the terminal will be blank. If anyfile has been changed/corrupted since recording the hash, it'll show up. 

# Recover the file
To recover the file `foo.bar`, you must have `foo.bar.frozen`. 
Run 
```
melt.sh foo.bar.frozen > foo_recovered.bar
```

# Limitation
Copying pasting the 3 files everytime is a hassle. I'm working on something better. 

For some reason, png files cannot be recovered. In somecases, I see files with spaces in their filename does do so well. 

# Disclaimer
I am not liable for any data loss you might have on your computer. This script doesn't come with any guarantee. 