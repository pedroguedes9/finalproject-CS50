from flask import Blueprint, request, render_template, redirect, url_for
from flask_login import login_user, login_required, logout_user
from db import db
from models import Users
from werkzeug.security import generate_password_hash, check_password_hash

auth_bp = Blueprint("auth", __name__, template_folder="templates")

@auth_bp.route("/register",methods = ["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        email = request.form.get("email")
        password = request.form.get("password")
        phone = request.form.get("phone")

        hashed_password = generate_password_hash(password)
        new_user = Users(username=username, email=email, password=hashed_password, phone_number=phone)
        db.session.add(new_user)
        db.session.commit()

        login_user(new_user)

        return redirect("/")
    else:
        return render_template("register.html")


@auth_bp.route("/login", methods=["POST", "GET"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        user = Users.query.filter_by(username=username).first()
        if not user or not check_password_hash(user.password, password):
            return "Nome de usuario ou senha incorretos"

        login_user(user)
        
        return redirect("/")
    else:
        return render_template("login.html")
    


@auth_bp.route("/logout", methods = ["GET"])
@login_required
def logout():
    logout_user()
    return redirect("/")