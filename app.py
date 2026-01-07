import os,uuid
from flask import Flask,render_template,render_template_string,request,send_from_directory,send_file,redirect,session,url_for,Response
import requests
from werkzeug.security import check_password_hash,generate_password_hash
from sqlalchemy import func
import io,zipfile
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.utils import secure_filename
app=Flask(__name__)

DATABASE_URL = os.getenv("DATABASE_URL")
PYANYWHERE_UPLOAD_URL = "https://wf5528.pythonanywhere.com/upload"
PYANYWHERE_LIST_URL   = "https://wf5528.pythonanywhere.com/list"
PYANYWHERE_SECRET     = "aa"
if DATABASE_URL:
    if DATABASE_URL.startswith("postgres://"):
        DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)
    app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URL
else:
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///local.db"

    app.config["SQLALCHEMY_BINDS"] = {
        "accounts": "sqlite:///accounts.db",
        "cards": "sqlite:///cards.db",
        "medias": "sqlite:///medias.db"
    }

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db=SQLAlchemy(app )
app.secret_key=os.urandom(32)
UPLOAD_PASSWORD=generate_password_hash("ff'gho113")
ADMIN_PASSWORD_HASH = generate_password_hash("koalfret4938(poxz'')")
UPLOAD_FOLDER = "/home/wf5528/infinitecloud_api/uploads"
app.config["UPLOAD_FOLDER"]="uploads"
ALLOWED={"png","jpg","jpeg","mp4","mov","pdf","webp","mp3"}
app.config["MAX_CONTENT_LENGTH"]=50*1024*1024
class Account(db.Model):
    __bind_key__="accounts"
    __tablename__="accounts_table"
    name=db.Column(db.String(20),nullable=False,unique=True)
    password=db.Column(db.String(100),nullable=False)
    id=db.Column(db.Integer,primary_key=True)
    def __repr__(self):
        return f"<Account {self.id}"
class Card(db.Model):
    __bind_key__="cards"
    __tablename__="card_table"
    title=db.Column(db.String(100),nullable=False)
    subtitle=db.Column(db.String(100),nullable=False)
    text=db.Column(db.String(600),nullable=False)
    id=db.Column(db.Integer,primary_key=True)
    def __repr__(self):
        return f"<Card {self.id}>"
class Media(db.Model):
    __bind_key__="medias"
    __tablename__="medias_table"
    id=db.Column(db.Integer,primary_key=True)
    original_name=db.Column(db.String(200))
    stored_name=db.Column(db.String(200))
    data=db.Column(db.LargeBinary)
    created_at=db.Column(db.DateTime,default=datetime.utcnow)
    download_count=db.Column(db.Integer,default=0)
    is_private = db.Column(db.Boolean, default=False)  # 🔒 gizli mi
    owner_session = db.Column(db.String(100))         

def send_to_pythonanywhere(filename, file_bytes):
    try:
        r = requests.post(
            PYANYWHERE_UPLOAD_URL,
            files={"file": (filename, file_bytes)},
            headers={"X-SECRET": PYANYWHERE_SECRET},
            timeout=10
        )
        print("STATUS:", r.status_code)
        print("TEXT:", r.text)
    except Exception as e:
        print("ERR:", e)


def allowed(filename):
    return "." in filename and filename.rsplit(".",1)[1].lower() in ALLOWED
@app.route("/")
def projects():
    return render_template("projects.html")
@app.route("/infinitecloud")
def cloud():
    return render_template("home_cloud.html")
@app.route("/__reset_db__")
def reset_db():
    if not session.get("can_delete"):
        return redirect("/infinitecloud/reset-login")
    
    with app.app_context():
        db.drop_all()
        db.create_all()
        db.create_all(bind="accounts")
        db.create_all(bind="cards")
        db.create_all(bind="medias")
    
    return "DB sıfırlandı ✅"

@app.route("/camsepeti/home")
def home_shop():
    if "user_id" not in session:
        return redirect("/camsepeti")
    return render_template("home.html")
@app.route("/camsepeti/sepete_ekle",methods=["POST"])
def sepete_ekle():
    if "user_id" not in session:
        return redirect("/camsepeti")
    urun={
        "ad": request.form["ad"],
        "fiyat": request.form["fiyat"],
        "resim":request.form["resim"]
    }
    if "sepet" not in session:
        session["sepet"]=[]
    sepet=session["sepet"]
    sepet.append(urun)
    session["sepet"]=sepet
    return redirect("/camsepeti/home")
@app.route("/camsepeti/sepet_sil", methods=["POST"])
def sepet_sil():
    if "user_id" not in session:
        return redirect("/camsepeti")
    index = int(request.form["index"])

    sepet = session.get("sepet", [])

    if 0 <= index < len(sepet):
        sepet.pop(index)
        session["sepet"] = sepet

    return redirect("/camsepeti/sepet")
@app.route("/camsepeti/buy_success",methods=["POST"])
def buy_success():
    if "user_id" not in session:
        return redirect("/camsepeti")
    return render_template("buy_success.html")
@app.route("/camsepeti/sepet")
def sepet():
    if "user_id" not in session:
        return redirect("/camsepeti")
    return render_template("sepet.html",sepet=session.get("sepet"))
@app.route("/camsepeti/buy")
def buy():
    if "user_id" not in session:
        return redirect("camsepeti")
    return render_template("buy.html")
@app.route("/camsepeti/register",methods=["GET","POST"])
def register():
    if request.method=="POST":
        try:
            name=request.form["name"]
            password=request.form["password"]

            hashed_pw=generate_password_hash(password)
            new_user=Account(name=name,password=hashed_pw)
            db.session.add(new_user)
            db.session.commit()
        except:
            return "Bu kullanıcı adı zaten var"
        return redirect("/camsepeti")
    return render_template("register.html")
@app.route("/camsepeti",methods=["GET","POST"])
def login():
    if request.method=="POST":
        name=request.form["name"]
        password=request.form["password"]
        user=Account.query.filter_by(name=name).first()
        if user and check_password_hash(user.password,password):
            session["user_id"]=user.id
            return redirect("/camsepeti/home")
        else:
            return "Hatalı giriş❌"
    return render_template("login.html")
@app.route("/camsepeti/logout")
def logout():
    session.clear()
    return redirect("/camsepeti")
@app.route("/infinitecloud/upload", methods=["GET", "POST"])
def upload():
    msg = ""

    if request.method == "POST":
        if not check_password_hash(UPLOAD_PASSWORD, request.form["password"]):
            return render_template("upload.html", msg="❌ Şifre yanlış")

        file = request.files.get("file")
        if not file or not allowed(file.filename):
            return render_template("upload.html", msg="❌ Geçersiz dosya")

        original_name = secure_filename(file.filename)
        ext = original_name.rsplit(".", 1)[1].lower()

        exists = Media.query.filter_by(original_name=original_name).first()
        stored_name = f"{uuid.uuid4()}.{ext}" if exists else original_name

        is_private = "is_private" in request.form

        # uploader session
        if "uploader_id" not in session:
            session["uploader_id"] = str(uuid.uuid4())

        file_bytes = file.read()

        media = Media(
            original_name=original_name,
            stored_name=stored_name,
            data=file_bytes,
            is_private=is_private,
            owner_session=session["uploader_id"]
        )

        db.session.add(media)
        db.session.commit()

        send_to_pythonanywhere(original_name, file_bytes)
        msg = "✅ Dosya yüklendi"

    return render_template("upload.html", msg=msg)

@app.route("/infinitecloud/files/<int:media_id>/download")
def download_file(media_id):
    media = Media.query.get_or_404(media_id)

    if media.is_private:
        if session.get("can_delete") is not True and media.owner_session != session.get("uploader_id"):
            return "❌ Bu dosya gizli", 403

    media.download_count += 1
    db.session.commit()

    return send_file(
        io.BytesIO(media.data),
        as_attachment=True,
        download_name=media.original_name
    )

@app.route("/infinitecloud/files/<int:media_id>")
def look(media_id):
    media = Media.query.get_or_404(media_id)

    if media.is_private:
        if session.get("can_delete") is not True and media.owner_session != session.get("uploader_id"):
            return "❌ Bu dosya gizli", 403

    return send_file(
        io.BytesIO(media.data),
        as_attachment=False,
        download_name=media.original_name
    )

@app.route("/infinitecloud/files/<int:media_id>/delete")
def delete_file(media_id):
    if not session.get("can_delete"):
        return redirect("/infinitecloud/reset-login")
    media=Media.query.get_or_404(media_id)
    db.session.delete(media)
    db.session.commit()
    return redirect("/infinitecloud/files")
@app.route("/infinitecloud/reset-login", methods=["GET", "POST"])
def reset_login():
    msg = ""
    if request.method == "POST":
        if check_password_hash(ADMIN_PASSWORD_HASH, request.form["password"]):
            session["can_reset"] = True
            session["can_delete"]=True
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
    uploader_id = session.get("uploader_id")
    is_admin = session.get("can_delete", False)

    if is_admin:
        medias = Media.query.all()
    else:
        medias = Media.query.filter(
            (Media.is_private == False) |
            (Media.owner_session == uploader_id)
        ).all()

    files_count = len(medias)

    pa_files = []
    try:
        r = requests.get(
            os.getenv("PYANYWHERE_LIST_URL"),
            headers={"X-SECRET": os.getenv("PYANYWHERE_SECRET")},
            timeout=5
        )
        pa_files = r.json().get("files", [])
    except:
         pass

    return render_template(
        "files.html",
        files=medias,
        files_count=files_count,
        can_reset=session.get("can_reset", False),
        can_delete=is_admin,
        pa_files=pa_files
    )


@app.route("/infinitecloud/files/download_all")
def download_all():
    medias = Media.query.all()
    if not medias:
        return "Hiç dosya yok."

    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w") as zip_file:
        for media in medias:
            zip_file.writestr(media.original_name, media.data)

    zip_buffer.seek(0)

    return send_file(
        zip_buffer,
        as_attachment=True,
        download_name="all_files.zip",
        mimetype="application/zip"
    )
# Sistemler
@app.route('/sitemap.xml', methods=['GET'])
def sitemap():
    sitemap_xml = """<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url>
    <loc>https://www.infinitesoft-tr.com/</loc>
  </url>
</urlset>
"""
    return Response(sitemap_xml, mimetype='application/xml')
@app.route("/infinitecloud/files/pa/download/<filename>")
def pa_download(filename):
    r = requests.get(
        f"https://wf5528.pythonanywhere.com/download/{filename}",
        headers={"X-SECRET": PYANYWHERE_SECRET},
        stream=True
    )

    if r.status_code != 200:
        return "PA download failed", 404

    return Response(
        r.content,
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"'
        }
    )
@app.route("/infinitecloud/pa/delete/<filename>", methods=["POST"])
def pa_delete(filename):
    r = requests.post(
        f"https://wf5528.pythonanywhere.com/delete/{filename}",
        headers={"X-SECRET": PYANYWHERE_SECRET},
        timeout=5
    )

    if r.status_code == 200:
        return redirect("/infinitecloud/files")
    return "Silinemedi", 400

if __name__=="__main__":
    app.run()
