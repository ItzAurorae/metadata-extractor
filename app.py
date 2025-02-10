from flask import Flask, render_template, request, jsonify
from PIL import Image, ExifTags
import os
import piexif
import json

app = Flask(__name__)

UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'bmp', 'webp'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def extract_metadata(image_path):
    metadata = {}

    try:
        image = Image.open(image_path)
        metadata["Format"] = image.format
        metadata["Mode"] = image.mode
        metadata["Size"] = f"{image.width}x{image.height} pixels"
        metadata["DPI"] = image.info.get("dpi", "Unknown")
        metadata["Bit Depth"] = image.mode
        metadata["Compression"] = image.info.get("compression", "None")

        # Extract EXIF metadata
        exif_data = image._getexif()
        if exif_data:
            metadata["EXIF"] = {}
            for tag, value in exif_data.items():
                tag_name = ExifTags.TAGS.get(tag, tag)
                metadata["EXIF"][tag_name] = value

        # Extract ICC profile
        if image.info.get("icc_profile"):
            metadata["ICC Profile"] = "Available"

        # Extract XMP metadata
        if "XML:com.adobe.xmp" in image.info:
            metadata["XMP"] = image.info["XML:com.adobe.xmp"]

    except Exception as e:
        metadata["Error"] = str(e)

    return metadata

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"error": "No file uploaded."})

    file = request.files['file']

    if file.filename == '':
        return jsonify({"error": "No file selected."})

    if file and allowed_file(file.filename):
        filename = file.filename
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        metadata = extract_metadata(filepath)

        return jsonify({"filename": filename, "metadata": metadata})

    return jsonify({"error": "Invalid file type. Please upload an image."})

if __name__ == '__main__':
    app.run(debug=True)
