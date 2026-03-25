#!/usr/bin/env python3
import subprocess
import sys
import platform
from pathlib import Path
import shutil


# -------------------------
# Utilities
# -------------------------
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
        print("❌ ImageMagick not found")
        sys.exit(1)


# -------------------------
# Install dependencies
# -------------------------
def install_dependencies():

    system = platform.system()

    print(f"\n🖥 Detected system: {system}")

    if system == "Linux":

        if not command_exists("dcraw"):
            print("📦 Installing dcraw…")
            run("sudo apt update && sudo apt install -y dcraw")

        if not command_exists("magick") and not command_exists("convert"):
            print("📦 Installing ImageMagick…")
            run("sudo apt install -y imagemagick")

        if not command_exists("exiftool"):
            print("📦 Installing ExifTool…")
            run("sudo apt install -y libimage-exiftool-perl")

    elif system == "Darwin":

        if not command_exists("brew"):
            print("❌ Homebrew is not installed")
            sys.exit(1)

        if not command_exists("dcraw"):
            run("brew install dcraw")

        if not command_exists("magick") and not command_exists("convert"):
            run("brew install imagemagick")

        if not command_exists("exiftool"):
            run("brew install exiftool")

    elif system == "Windows":

        print("⚠ Use WSL to run this script")
        sys.exit(1)

    else:

        print("❌ Unsupported operating system")
        sys.exit(1)


# -------------------------
# Read RAW orientation
# (force portrait orientation if horizontal)
# -------------------------
def get_rotation_from_raw(raw):

    try:

        result = subprocess.check_output(
            f'exiftool -CameraOrientation -Orientation "{raw}"',
            shell=True
        ).decode().lower()

        if "rotate 270" in result:
            return -90

        if "rotate 90" in result:
            return 90

        if "rotate 180" in result:
            return 180

        if "horizontal" in result:
            return -90  # force portrait orientation

    except:
        pass

    return -90  # fallback portrait orientation


# -------------------------
# Apply rotation
# -------------------------
def rotate_image_if_needed(jpg, im_cmd, rotation):

    tmp = jpg.with_suffix(".tmp.jpg")

    print(f"🔄 Applying rotation ({rotation}°): {jpg.name}")

    cmd_rotate = f'{im_cmd} "{jpg}" -rotate {rotation} "{tmp}"'
    subprocess.run(cmd_rotate, shell=True)

    tmp.replace(jpg)

    subprocess.run(
        f'exiftool -Orientation=1 -n -overwrite_original "{jpg}"',
        shell=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )


# -------------------------
# Batch processing
# -------------------------
def process_images():

    im_cmd = detect_imagemagick()
    print(f"🖼 ImageMagick detected: {im_cmd}")

    input_dir = Path(input("\n📂 RAW folder (.cr2): ").strip()).expanduser()
    output_dir = Path(input("📂 Output JPG folder: ").strip()).expanduser()

    if not input_dir.is_dir():

        print("❌ Invalid input folder")
        sys.exit(1)

    output_dir.mkdir(parents=True, exist_ok=True)

    raws = list(input_dir.glob("*.cr2")) + list(input_dir.glob("*.CR2"))

    if not raws:

        print("❌ No CR2 files found")
        sys.exit(1)

    print(f"\n📷 Files found: {len(raws)}\n")

    for raw in raws:

        jpg = output_dir / (raw.stem + ".jpg")

        # -------------------------
        # Skip if JPG already exists
        # -------------------------
        if jpg.exists():

            print(f"⏩ Skipped (already exists): {jpg.name}")
            continue

        print(f"➡ Processing: {raw.name}")

        # -------------------------
        # Read RAW orientation
        # -------------------------
        rotation = get_rotation_from_raw(raw)

        # -------------------------
        # RAW development
        # -------------------------
        cmd = (
            f'dcraw -c -t 0 -w -H 0 -o 1 -q 3 '
            f'-g 2.2 4.5 -b 1.12 -n 8 "{raw}" | '
            f'{im_cmd} ppm:- -quality 95 "{jpg}"'
        )

        subprocess.run(cmd, shell=True)

        # -------------------------
        # Copy EXIF metadata
        # -------------------------
        exif_cmd = (
            f'exiftool -TagsFromFile "{raw}" '
            f'-all:all -overwrite_original "{jpg}"'
        )

        subprocess.run(
            exif_cmd,
            shell=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )

        # -------------------------
        # Final rotation
        # -------------------------
        rotate_image_if_needed(jpg, im_cmd, rotation)

    print("\n✅ Processing finished")


# -------------------------
# Main
# -------------------------
def main():

    print("=== CR2 → JPG batch processing (dcraw) ===")

    install_dependencies()

    process_images()


if __name__ == "__main__":
    main()
