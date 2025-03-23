from flask import Flask, render_template, request, jsonify
from flask_cors import CORS  # Import CORS
from PIL import Image, ExifTags
import os

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

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
    except Exception as e:
        metadata["Error"] = str(e)
    return metadata

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"error": "No file uploaded."}), 400

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
