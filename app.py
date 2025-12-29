import os,uuid
from flask import Flask,render_template,render_template_string,request,send_from_directory,send_file,redirect,session
from werkzeug.security import check_password_hash,generate_password_hash
from sqlalchemy import func
import io,zipfile
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
app=Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://admin_infinitesofttr:kQcMy3cWCcj1gMgJWs3aMwb3XqwRFbnA@dpg-d58dlashg0os73bo9l4g-a/medias"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db=SQLAlchemy(app )
app.secret_key=os.urandom(32)
UPLOAD_PASSWORD=generate_password_hash("ff'gho113")
ADMIN_PASSWORD_HASH = generate_password_hash("koalfret4938(poxz'')")
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
        if not check_password_hash(UPLOAD_PASSWORD, request.form["password"]):

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
@app.route("/infinitecloud/reset-login", methods=["GET", "POST"])
def reset_login():
    msg = ""
    if request.method == "POST":
        if check_password_hash(ADMIN_PASSWORD_HASH, request.form["password"]):
            session["can_reset"] = True
            return redirect("/infinitecloud/files")
        else:
            msg = "❌ Admin şifre yanlış"
    return render_template("reset_login.html", msg=msg)

@app.route("/infinitecloud/reset", methods=["POST"])
def reset_files():
    if not session.get("can_reset"):
        return redirect("/infinitecloud/reset-login")

    medias = Media.query.all()
    for media in medias:
        db.session.delete(media)
    db.session.commit()

    session.pop("can_reset")
    return "✅ Tüm dosyalar silindi."

@app.route("/infinitecloud/files")
def files():
    files_count = db.session.query(func.count(Media.id)).scalar()
    medias = Media.query.all()
    return render_template(
        "files.html",
        files=medias,
        files_count=files_count,
        can_reset=session.get("can_reset", False)
    )
@app.route("/infinitecloud/files/download_all")
def download_all():
    medias = Media.query.all()
    if not medias:
        return "Hiç dosya yok."

    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w") as zip_file:
        for media in medias:
            zip_file.writestr(media.filename, media.data)

    zip_buffer.seek(0)

    return send_file(
        zip_buffer,
        as_attachment=True,
        download_name="all_files.zip",
        mimetype="application/zip"
    )
if __name__=="__main__":
    app.run()
