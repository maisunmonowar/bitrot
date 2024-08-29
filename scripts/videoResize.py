import os
import subprocess
import shutil
import argparse

def resize_media(input_path, output_path):
    # Create the "deleteLater" folder if it doesn't exist
    delete_later_folder = os.path.join(output_path, "deleteLater")
    os.makedirs(delete_later_folder, exist_ok=True)

    # Walk through the input path
    for root, dirs, files in os.walk(input_path):
        for filename in files:
            full_path = os.path.join(root, filename)
            base_name, ext = os.path.splitext(filename)

            # Check if it's an image or video
            if ext.lower() in (".jpg", ".jpeg", ".png"):
                # Get the folder name (e.g., "1024", "720p")
                folder_name = os.path.basename(root)
                try:
                    size = int(folder_name)
                except ValueError:
                    continue  # Skip folders with non-integer names

                # Resize the image using ImageMagick
                resized_filename = f"{base_name}_{size}px{ext}"
                resized_path = os.path.join(root, resized_filename)
                subprocess.run(["convert", full_path, "-resize", f"{size}x{size}", resized_path])

                # Move the original file to "deleteLater"
                shutil.move(full_path, os.path.join(delete_later_folder, filename))
                print(f"Resized image: {resized_filename}")

            elif ext.lower() in (".mp4", ".mkv", ".avi"):
                # Get the resolution from the folder name (e.g., "720p")
                folder_name = os.path.basename(root)
                resolution = folder_name.lower()

                # Resize the video using FFmpeg
                resized_filename = f"{base_name}_{resolution}{ext}"
                resized_path = os.path.join(root, resized_filename)
                subprocess.run(["ffmpeg", "-i", full_path, "-vf", f"scale={resolution}", resized_path])

                # Move the original file to "deleteLater"
                shutil.move(full_path, os.path.join(delete_later_folder, filename))
                print(f"Resized video: {resized_filename}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Resize images and videos based on folder names")
    parser.add_argument("input_folder", help="Path to the input folder containing media files")
    parser.add_argument("output_folder", help="Path to the output folder for resized files")
    args = parser.parse_args()

    resize_media(args.input_folder, args.output_folder)
