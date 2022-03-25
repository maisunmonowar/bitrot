import os
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

def main():
    directory = os.getcwd()
    freeze_files(directory)

if __name__ == '__main__':
    main()