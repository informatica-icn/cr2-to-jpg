#!/usr/bin/env python3
import subprocess
import sys
import platform
from pathlib import Path
import shutil

def command_exists(cmd):
    return shutil.which(cmd) is not None

def run(cmd):
    subprocess.run(cmd, shell=True, check=True)

def detect_imagemagick():
    if command_exists("magick"):
        return "magick"
    elif command_exists("convert"):
        return "convert"
    else:
        print("ImageMagick not found")
        sys.exit(1)

def install_dependencies():
    system = platform.system()

    if system == "Linux":
        if not command_exists("dcraw"):
            run("sudo apt update && sudo apt install -y dcraw")
        if not command_exists("magick") and not command_exists("convert"):
            run("sudo apt install -y imagemagick")
        if not command_exists("exiftool"):
            run("sudo apt install -y libimage-exiftool-perl")

    elif system == "Darwin":
        if not command_exists("brew"):
            print("Homebrew not installed")
            sys.exit(1)
        if not command_exists("dcraw"):
            run("brew install dcraw")
        if not command_exists("magick") and not command_exists("convert"):
            run("brew install imagemagick")
        if not command_exists("exiftool"):
            run("brew install exiftool")

    else:
        print("Unsupported system")
        sys.exit(1)

def rotate_image(jpg, im_cmd):
    tmp = jpg.with_suffix(".tmp.jpg")
    cmd_rotate = f'{im_cmd} "{jpg}" -rotate -90 "{tmp}"'
    subprocess.run(cmd_rotate, shell=True)
    tmp.replace(jpg)

    cmd_exif = f'exiftool -Orientation=1 -n -overwrite_original "{jpg}"'
    subprocess.run(cmd_exif, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def process_images():
    im_cmd = detect_imagemagick()

    input_dir = Path(input("Input folder (.CR2): ").strip()).expanduser()
    output_dir = Path(input("Output folder (.JPG): ").strip()).expanduser()

    if not input_dir.is_dir():
        print("Invalid input folder")
        sys.exit(1)

    output_dir.mkdir(parents=True, exist_ok=True)

    raws = list(input_dir.glob("*.cr2")) + list(input_dir.glob("*.CR2"))

    if not raws:
        print("No CR2 files found")
        sys.exit(1)

    for raw in raws:
        jpg = output_dir / (raw.stem + ".jpg")

        cmd = (
            f'dcraw -c -w -H 0 -o 1 -q 3 '
            f'-g 2.2 4.5 -b 1.12 -n 8 "{raw}" | '
            f'{im_cmd} ppm:- -quality 95 "{jpg}"'
        )

        subprocess.run(cmd, shell=True)

        exif_cmd = (
            f'exiftool -TagsFromFile "{raw}" '
            f'-all:all -overwrite_original "{jpg}"'
        )

        subprocess.run(exif_cmd, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        rotate_image(jpg, im_cmd)

    print("Done")

def main():
    print("CR2 to JPG batch processor")
    install_dependencies()
    process_images()

if __name__ == "__main__":
    main()
