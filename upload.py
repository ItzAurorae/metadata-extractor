from flask import Flask, render_template, request, jsonify
from PIL import Image, ExifTags
import piexif
import os

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
        # Open the image file
        image = Image.open(image_path)

        # General image information
        metadata["Format"] = image.format
        metadata["Mode"] = image.mode
        metadata["Size"] = f"{image.width}x{image.height} pixels"
        metadata["DPI"] = image.info.get("dpi", "Unknown")  # Default to "Unknown" if DPI is not available
        metadata["Bit Depth"] = image.mode
        metadata["Compression"] = image.info.get("compression", "None")  # Default to "None" if compression is not available

        # Extract EXIF metadata using piexif (more robust than _getexif)
        try:
            exif_dict = piexif.load(image_path)
            if exif_dict:
                metadata["EXIF"] = {}
                for ifd in exif_dict:
                    for tag, value in exif_dict[ifd].items():
                        tag_name = ExifTags.TAGS.get(tag, tag)
                        metadata["EXIF"][tag_name] = value
        except Exception as exif_error:
            metadata["EXIF"] = f"Error reading EXIF: {str(exif_error)}"

        # Extract ICC profile if available
        if "icc_profile" in image.info:
            metadata["ICC Profile"] = "Available"
        else:
            metadata["ICC Profile"] = "Not Available"

        # Extract XMP metadata if available
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
        return jsonify({"error": "No file uploaded."}), 400  # 400 for bad request

    file = request.files['file']

    if file.filename == '':
        return jsonify({"error": "No file selected."}), 400

    if file and allowed_file(file.filename):
        filename = file.filename
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        metadata = extract_metadata(filepath)

        return jsonify({"filename": filename, "metadata": metadata}), 200

    return jsonify({"error": "Invalid file type. Please upload an image."}), 400


if __name__ == "__main__":
    app.run(debug=True)
