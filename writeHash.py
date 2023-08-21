import os
import argparse
import subprocess

def write_hash(directory):
    for filename in os.listdir(directory):     
        if os.path.isfile(directory + "/" +filename):
            # print("File: ", directory + "/" + filename)
            out = subprocess.Popen(['md5sum', directory + "/" + filename], stdout = subprocess.PIPE, stderr = subprocess.STDOUT)
            stdout, stderr = out.communicate()
            # print("have to do something with: "+ stdout[:32].decode())
            if filename[-3:] != 'hsh':
                with open(directory + "/" + "." + filename+".hsh", 'w') as f:
                    if f.write(stdout[:32].decode()):
                        # print("File write ok.")
                        continue
                    else:
                        print("Error writing to file.")
                        print("File: ", directory + "/" + filename)
        else:
            # print("Directory: ", directory + "/" + filename)
            
            # print(filename, " is a directory")
            write_hash(directory + "/" + filename)
    return 0

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Write hash files.')
    parser.add_argument('-d', '--directory', type=str, help='Directory to write hash files.', default=os.getcwd())
    args = parser.parse_args()

    if write_hash(args.directory):
        print("Error running write_hash")
    else:
        print("All done. Ok. ")