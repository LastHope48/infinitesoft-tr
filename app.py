import os,uuid
from flask import Flask,render_template,render_template_string,request,send_from_directory,send_file
import io,zipfile
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
app=Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://admin_infinitesofttr:kQcMy3cWCcj1gMgJWs3aMwb3XqwRFbnA@dpg-d58dlashg0os73bo9l4g-a:5432/infinitesoft_cloud'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db=SQLAlchemy(app )
UPLOAD_PASSWORD="ff'gho113"
app.config["UPLOAD_FOLDER"]="uploads"
ALLOWED={"png","jpg","jpeg","mp4","mov"}
app.config["MAX_CONTENT_LENGTH"]=50*1024*1024
class Media(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    filename=db.Column(db.String(200))
    data=db.Column(db.LargeBinary)
    created_at=db.Column(db.DateTime,default=datetime.utcnow)
def allowed(filename):
    return "." in filename and filename.rsplit(".",1)[1].lower() in ALLOWED
@app.route("/")
def projects():
    return render_template("projects.html")
@app.route("/infinitecloud")
def cloud():
    return render_template("home_cloud.html")
@app.route("/infinitecloud/upload", methods=["GET", "POST"])
def upload():
    msg = ""
    if request.method == "POST":
        if request.form["password"] != UPLOAD_PASSWORD:
            msg = "❌ Şifre yanlış"
        else:
            file = request.files["file"]
            if file and allowed(file.filename):
                # Dosya adı oluştur
                ext = file.filename.rsplit(".", 1)[1].lower()
                unique_name = f"{uuid.uuid4()}.{ext}"

                # Dosyayı veritabanına kaydet
                media = Media(filename=unique_name, data=file.read())
                db.session.add(media)
                db.session.commit()

                msg = "✅ Dosya veritabanına kaydedildi"
            else:
                msg = "❌ Geçersiz dosya"
    return render_template("upload.html", msg=msg)
@app.route("/infinitecloud/files/<int:media_id>/download")
def download_file(media_id):
    media = Media.query.get_or_404(media_id)
    return send_file(
        io.BytesIO(media.data),        # Binary veriyi oku
        as_attachment=True,            # İndirme olarak sun
        download_name=media.filename   # Dosya adı
    )
@app.route("/infinitecloud/files")
def files():
    medias=Media.query.all()
    return render_template("files.html",files=medias)
@app.route("/infinitecloud/files/download_all")
def download_all():
    medias = Media.query.all()
    
    if not medias:
        return "Hiç dosya yok."
    
    # Zip buffer oluştur
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w") as zip_file:
        for media in medias:
            zip_file.writestr(media.filename, media.data)  # Veritabanındaki veriyi zip'e ekle
    
    zip_buffer.seek(0)
    
    # Veritabanını temizle
    for media in medias:
        db.session.delete(media)
    db.session.commit()
    
    # Zip dosyasını indir
    return send_file(
        zip_buffer,
        as_attachment=True,
        download_name="all_files.zip",
        mimetype="application/zip"
    )
with app.app_context():
    db.create_all()
if __name__=="__main__":
    app.run()
