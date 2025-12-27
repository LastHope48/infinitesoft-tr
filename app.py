import os,uuid
from flask import Flask,render_template,render_template_string,request
from flask_sqlalchemy import SQLAlchemy
app=Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///diary.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db=SQLAlchemy(app )
UPLOAD_PASSWORD="ff'gho113"
app.config["UPLOAD_FOLDER"]="uploads"
ALLOWED={"png","jpg","jpeg","mp4","mov"}
app.config["MAX_CONTENT_LENGTH"]=50*1024*1024
def allowed(filename):
    return "." in filename and filename.rsplit(".",1)[1].lower() in ALLOWED
HTML="""
<form method="post" enctype="multipart/form-data">
    <input type="password" name="password" placeholder="Şifre" required><br><br>
    <input type="file" name="file" required><br><br>
    <button>Yükle</button>
</form>
<p>{{msg}}</p>
"""


@app.route("/")
def projects():
    return render_template("projects.html")
@app.route("/infinitecloud")
def cloud():
    return render_template("home_cloud.html")
@app.route("/infinitecloud/upload",methods=["GET","POST"])
def upload():
    msg=""
    if request.method=="POST":
        if request.form["password"]!=UPLOAD_PASSWORD:
            msg="❌ Şifre yanlış"
        else:
            file=request.files["file"]
            if file and allowed(file.filename):
                os.makedirs(app.config["UPLOAD_FOLDER"],exist_ok=True)
                ext=file.filename.rsplit(".",1)[1]
                name=f"{uuid.uuid4()}.{ext}"
                file.save(os.path.join(app.config["UPLOAD_FOLDER"],name))
                msg="✅ Dosya yüklendi"
            else:
                msg="❌ Geçersiz dosya"
    return render_template("upload.html",msg=msg)
if __name__=="__main__":
    app.run(debug=True)
