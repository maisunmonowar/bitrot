import subprocess
import os

def check_hash(directory):
    for filename in os.listdir(directory):     
        if os.path.isfile(directory + "/" +filename):
            # print("File: ", directory + "/" + filename)
            out = subprocess.Popen(['md5sum', directory + "/" + filename], stdout = subprocess.PIPE, stderr = subprocess.STDOUT)
            stdout, stderr = out.communicate()
            if filename[-3:] != 'hsh':
                try:
                    with open(directory + "/" + "." + filename+".hsh", 'r') as f:
                        hashh = f.readline()
                        if stdout[:32].decode() == hashh:
                            # print("No bit rot.")
                            continue
                        else:
                            print("BIT ROTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTT.")
                            print("File: ", directory + "/" + filename)
            
                except FileNotFoundError:
                    print("Are you sure you wrote the hash files before?")
                    raise
        else:
            # print("Directory: ", directory + "/" + filename)
            
            # print(filename, " is a directory")
            check_hash(directory + "/" + filename)
    return 0

def main():
    cwd = os.getcwd()
    if check_hash(cwd):
        print("Error running check_hash")
    

if __name__ == '__main__':
    main()