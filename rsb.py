"""
RSB - Remote Storage Builder: File Archiver/Extractor Utility

This module provides a command-line interface for archiving and extracting files
using Docker containers. It offers two main operations:

    1. FREEZE (--freeze/-f): Pack individual files or directories into .frozen archives
    2. MELT (--melt/-m): Extract contents from .frozen archives back to .melted files

The module uses Docker containers to isolate the archiving/extracting logic, 
ensuring a consistent environment across different host systems.

Usage:
    python rsb.py --freeze [-i|--file <path>] | [-d|--directory <path>]
    python rsb.py --melt   [-i|--file <path>] | [-d|--directory <path>]

Dependencies:
    - Docker (running and buildx enabled)
    - freeze.sh script inside the container for archiving
    - melt.sh script inside the container for extracting

Outputs:
    - frozen_data/ : Stores .frozen archive files (created during FREEZE)
    - melted_data/: Stores extracted output files (created during MELT)
"""
import argparse 
import os


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Importatant file archiver/extractor")
    parser.add_argument("--freeze", "-f", action="store_true", help="Freeze files into a single archive"
                        )    
    parser.add_argument("--melt", "-m", action="store_true", help="Extract files from an archive")
    parser.add_argument("--file", "-i", type=str, help="Input file or directory")
    parser.add_argument("--directory", "-d", type=str, help="input directory")

    args = parser.parse_args()

    # you must provide either --freeze or --melt. either file or directory must be provided
    if not (args.freeze or args.melt):
        parser.error("You must provide either --freeze or --melt")
    if not (args.file or args.directory):
        parser.error("You must provide either --file or --directory")

    os.makedirs("frozen_data", exist_ok=True)
    os.makedirs("melted_data", exist_ok=True)

    # Build the docker image
    os.system("docker build -t rsb .")

    if args.freeze:
        if args.file:
            input_path = os.path.abspath(args.file)
            output_dir = os.path.abspath("frozen_data")
            filename = os.path.basename(args.file)
            # Mount input file and output dir, run freeze.sh, pipe output to output dir
            os.system(
                f"docker run --rm "
                f"-v {input_path}:/data/input_file "
                f"-v {output_dir}:/data/output "
                f"rsb bash -c 'usr/local/bin/freeze.sh /data/input_file > /data/output/{filename}.frozen'"
            )
        elif args.directory:
            input_dir = os.path.abspath(args.directory)
            output_dir = os.path.abspath("frozen_data")
            # For directories, you may want to handle multiple files
            os.system(
                f"docker run --rm "
                f"-v {input_dir}:/data/input_dir "
                f"-v {output_dir}:/data/output "
                f"rsb bash -c 'for f in /data/input_dir/*; do ./freeze.sh \"$f\" > /data/output/$(basename \"$f\").frozen; done'"
            )
    elif args.melt:
        if args.file:
            input_path = os.path.abspath(args.file)
            output_dir = os.path.abspath("melted_data")
            filename = os.path.basename(args.file)
            os.system(
                f"docker run --rm "
                f"-v {input_path}:/data/input_file "
                f"-v {output_dir}:/data/output "
                f"rsb bash -c './melt.sh /data/input_file > /data/output/{filename}.melted'"
            )
        elif args.directory:
            input_dir = os.path.abspath(args.directory)
            output_dir = os.path.abspath("melted_data")
            os.system(
                f"docker run --rm "
                f"-v {input_dir}:/data/input_dir "
                f"-v {output_dir}:/data/output "
                f"rsb bash -c 'for f in /data/input_dir/*; do ./melt.sh \"$f\" > /data/output/$(basename \"$f\").melted; done'"
            )