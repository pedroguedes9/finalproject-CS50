from flask import Blueprint, request, render_template, redirect, url_for
from flask_login import LoginManager, login_user, login_required
from db import db
from models import Users

auth_bp = Blueprint("auth", __name__)

@app.route("/",methods = ["GET", "POST"])
def index():
    if request.method == "POST":
        username = request.form.get("username")
        email = request.form.get("email")
        password = request.form.get("password")
        telefone = request.form.get("telefone")

        new_user = Users(username=username, email=email, password=hash(password), telefone_number=telefone)
        db.session.add(new_user)
        db.session.commit()

        login_user(new_user)

        return redirect("/")
    else:
        users = db.session.query(Users).all()
        return render_template("index.html", users=users)