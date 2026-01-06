from flask import Flask, request, jsonify, send_from_directory, abort
import os

app = Flask(__name__)

UPLOAD_DIR = "/home/username/infinitecloud_api/storage"
SECRET = "SENIN_SECRET_KEYIN"

os.makedirs(UPLOAD_DIR, exist_ok=True)

def check_secret():
    return request.headers.get("X-SECRET") == SECRET

@app.route("/upload", methods=["POST"])
def upload():
    if not check_secret():
        abort(403)

    file = request.files.get("file")
    if not file:
        return "Dosya yok", 400

    file.save(os.path.join(UPLOAD_DIR, file.filename))
    return "OK"

@app.route("/list")
def list_files():
    if not check_secret():
        abort(403)

    return jsonify({
        "files": os.listdir(UPLOAD_DIR)
    })

@app.route("/download/<name>")
def download(name):
    if not check_secret():
        abort(403)

    return send_from_directory(UPLOAD_DIR, name, as_attachment=True)

@app.route("/delete/<name>")
def delete(name):
    if not check_secret():
        abort(403)

    path = os.path.join(UPLOAD_DIR, name)
    if os.path.exists(path):
        os.remove(path)
    return "Silindi"
