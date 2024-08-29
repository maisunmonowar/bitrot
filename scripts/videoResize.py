import os
import argparse
import subprocess
   
def resizeVideo(fullpath):
    print(f'this video file needs to be resized {os.path.basename(itemss)} at {os.path.dirname(itemss)}')
    
    

def resizeImage(fullpath):
    """Resizes an image based on the target resolution specified in the folder name.

    Args:
        fullpath (str): The full path to the image file.
    """

    target_path = os.path.dirname(fullpath)
    target_resolution = int(os.path.basename(target_path))
    target_name = f"{os.path.splitext(os.path.basename(fullpath))[0]}_{target_resolution}{os.path.splitext(fullpath)[1]}"

    # Resize the image using ImageMagick (adjust the command as needed)
    subprocess.run(["convert", fullpath, "-resize", f"{target_resolution}x{target_resolution}", target_path + "/" + target_name])

    # Move the original file to a "deleteLater" folder
    move_original_file_to = os.path.join(target_path, "..", "deleteLater")
    os.makedirs(move_original_file_to, exist_ok=True)
    os.rename(fullpath, os.path.join(move_original_file_to, os.path.basename(fullpath)))
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Resize images and videos based on folder names")
    parser.add_argument("-i", "--input_folder", help="Path to the input folder containing media files")
    args = parser.parse_args()
    
    imageResizeFolderNames = ["128", "256", "512", "1024", "2048"]
    videoResizeFolderNames = ["240p", "360p", "720p", "1080p", "2k", "4k"]

    imageToResize = []
    videoToResize = []
    # Walk through the input folder
    for root, dirs, files in os.walk(args.input_folder):
        for filename in files:
            full_path = os.path.join(root, filename)

            # Check if it's an image file
            if filename.lower().endswith((".jpg", ".jpeg", ".png")):
                imageToResize.append(os.path.join(root, filename))
                
            # Check if it's an video file
            if filename.lower().endswith((".mp4", ".mkv", ".mov")):
                videoToResize.append(os.path.join(root, filename))
                
    for itemss in imageToResize:
        folderName = os.path.basename(os.path.dirname(itemss))
        if folderName in imageResizeFolderNames:
            resizeImage(itemss)
    
    print()
    for itemss in videoToResize:
        folderName = os.path.basename(os.path.dirname(itemss))
        if folderName in videoResizeFolderNames:
            resizeVideo(itemss)
            
        
