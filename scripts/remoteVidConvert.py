import argparse
import zipfile
import os
import fnmatch
import shutil
import ffmpeg

def pathList_toconvert(filelist):
    for itemmss in filelist:
        b = os.path.split( os.path.dirname(itemmss))[-1]
        print(f'file: {itemmss}. base: {b}')
        convert_video(itemmss, b)
        print()

def convert_video(input_path, target_resolution):
    # Define the output path
    if not os.path.isfile(input_path):
        print("asdfkajsd;lfkja;lsdkfj")
        exit(-1)
    dir_name, file_name = os.path.split(input_path)
    file_base, file_ext = os.path.splitext(file_name)
    output_path = os.path.join(dir_name, f"{file_base}_resized.mp4")
    delete_later_dir = os.path.join(dir_name, 'deletelater')

    # Create 'deletelater' directory if it doesn't exist
    if not os.path.exists(delete_later_dir):
        os.makedirs(delete_later_dir)
    
    # Get the current resolution of the video
    probe = ffmpeg.probe(input_path)
    video_stream = next((stream for stream in probe['streams'] if stream['codec_type'] == 'video'), None)
    width = int(video_stream['width'])
    height = int(video_stream['height'])
    current_resolution = f"{height}p"

    # Determine if resizing is needed
    if target_resolution != 'av1' and int(target_resolution[:-1]) <= int(current_resolution[:-1]):
        print(f"No need to resize. Current resolution ({current_resolution}) is higher or equal to target resolution ({target_resolution}).")
        return

    # Set the target resolution
    if target_resolution != 'av1':
        target_height = int(target_resolution[:-1])
        target_width = int(width * (target_height / height))
    else:
        target_height = height
        target_width = width

    # Convert or transcode the video
    try:
        if target_resolution == 'av1':
            ffmpeg.input(input_path).output(output_path, vcodec='libaom-av1', crf=20, cpu_used=4).run()
        else:
            ffmpeg.input(input_path).output(output_path, vf=f'scale={target_width}:{target_height}', vcodec='libaom-av1', crf=20, cpu_used=4).run()
        
        # Move the original file to 'deletelater' directory
        shutil.move(input_path, os.path.join(delete_later_dir, file_name))
        print(f"Converted video saved to {output_path}. Original file moved to 'deletelater' directory.")
    except ffmpeg.Error as e:
        print(f"Error occurred: {e}")


def find_video_files(directory):
    video_extensions = ['*.mp4', '*.avi', '*.mkv', '*.mov', '*.flv', '*.wmv', '*.webm']
    video_files = []

    for root, dirs, files in os.walk(directory):
        for extension in video_extensions:
            for filename in fnmatch.filter(files, extension):
                video_files.append(os.path.abspath(os.path.join(root, filename)))

    return video_files

def extract_zip(filepath, password, extract_to="./tmp"):
    if not os.path.exists(extract_to):
        os.makedirs(extract_to)
    
    with zipfile.ZipFile(filepath, 'r') as zip_ref:
        zip_ref.extractall(path=extract_to, pwd=password.encode())

def main():
    parser = argparse.ArgumentParser(description="Extract a zip file to a specified directory.")
    parser.add_argument('--filepath', type=str, default='test.zip', help='Path to the zip file')
    parser.add_argument('--password', type=str, default='test', help='Password for the zip file')
    
    args = parser.parse_args()
    
#   extract_zip(args.filepath, args.password)
    fi = find_video_files('./tmp')
    pathList_toconvert(fi)

if __name__ == "__main__":
    main()
