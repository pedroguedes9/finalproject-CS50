import os
from flask import Flask, render_template, request, redirect, url_for
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from dotenv import load_dotenv
from db import db
from models import Users, Products, CartItems, OrderItems, Orders, Categories
import hashlib
from blueprints.carrinho.carrinho import carrinho_bp
from blueprints.produtos.produtos import produtos_bp
from blueprints.compras.compras import compras_bp

load_dotenv()

app = Flask(__name__)
app.secret_key = 'SECRET_KEY'
app.register_blueprint(produtos_bp, url_prefix="/produtos")
app.register_blueprint(carrinho_bp, url_prefix="/carrinho")
app.register_blueprint(compras_bp, url_prefix="/compras")
lm = LoginManager(app)
lm.login_view = 'index'
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///confeitaria.db"
db.init_app(app)

def hash(txt):
    hash_obj = hashlib.sha256(txt.encode('utf-8'))
    return hash_obj.hexdigest()

@lm.user_loader
def user_loader(id):
    user = db.session.query(Users).filter_by(id=id).first()
    return user

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

@app.route("/login", methods=["POST", "GET"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        
        user = db.session.query(Users).filter_by(username=username, password=hash(password)).first()
        if not user:
            return "Nome ou senha incorretos"

        login_user(user)
        
        return redirect("/")
    else:
        return render_template("login.html")
    
@app.route("/logout", methods = ["GET"])
@login_required
def logout():
    logout_user()
    return redirect("/")

@app.route("/delete", methods = ["POST"])
def delete():
    if request.method == "POST":
        id = request.form.get("id")
        user = db.session.query(Users).filter_by(id=id).first()
        db.session.delete(user)
        db.session.commit()
        return redirect("/")

@app.route("/change", methods = ["POST"])
def change():
    if request.method == "POST":
        id = request.form.get("id")
        new_name = request.form.get("new_name")
        user = db.session.query(Users).filter_by(id=id).first()
        user.username = new_name
        db.session.commit()
        return redirect("/")



with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run(debug=True)
