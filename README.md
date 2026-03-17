# CR2 to JPG Batch Processor

Python script to convert Canon RAW (.CR2) images into JPG with:
- dcraw (RAW processing)
- ImageMagick (conversion + rotation)
- ExifTool (metadata preservation)

## Features
- Batch processing
- EXIF metadata copy
- Forced 90° rotation
- Auto dependency install (Linux/macOS)

## Usage
```bash
chmod +x script.py
./script.py
```

## Requirements
- Python 3
- dcraw
- ImageMagick
- ExifTool
