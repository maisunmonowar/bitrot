import os
import argparse
import subprocess

def freeze_files(directory):
    for filename in os.listdir(directory):
        if filename.endswith(".hsh") or filename.endswith(".frozen") or filename.endswith(".py")or filename.endswith(".png"):
            #do nothing
            continue
        else:
            if os.path.isfile(directory + "/" +filename):
                print(os.path.join(directory, filename))
                out = subprocess.Popen(['freeze.sh', os.path.join(directory, filename)], stdout = subprocess.PIPE, stderr = subprocess.STDOUT)
                stdout, stderr = out.communicate()
            
                with open(directory + "/" + filename+".frozen", 'wb') as f:
                    f.write(stdout)
            else:
                freeze_files(os.path.join(directory, filename))


if __name__ == '__main__':
    # parse arguments
    parser = argparse.ArgumentParser(description='Freeze your files for preservation.')
    parser.add_argument('-d', '--directory', type=str, help='Directory where your desired files are stored.', default=os.getcwd())
    args = parser.parse_args()

    freeze_files(args.directory)
