import os
from flask import Flask, render_template, redirect
from flask_login import LoginManager, current_user
from flask_wtf.csrf import CSRFProtect
from db import db
from models import Users
from blueprints.cart.cart import cart_bp
from blueprints.products.products import products_bp
from blueprints.orders.orders import orders_bp
from blueprints.auth.auth import auth_bp
from blueprints.categories.categories import categories_bp
from dotenv import load_dotenv
from utils.decorators import admin_required

load_dotenv()


app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///confeitaria.db"
app.config['MAX_CONTENT_LENGTH'] = 2 * 1024 * 1024 #2MB

db.init_app(app)

login_manager = LoginManager(app)
login_manager.login_view = 'auth.login'
login_manager.login_message = "Por favor, faça login para acessar está página"
login_manager.login_message_category = "warning"

app.register_blueprint(products_bp, url_prefix="/products")
app.register_blueprint(cart_bp, url_prefix="/cart")
app.register_blueprint(orders_bp, url_prefix="/orders")
app.register_blueprint(auth_bp, url_prefix="/auth")
app.register_blueprint(categories_bp, url_prefix="/categories")

csrf = CSRFProtect(app)

@login_manager.user_loader
def load_user(user_id):
    user = db.session.query(Users).filter_by(id=user_id).first()
    return user

@app.route("/",methods=["GET"])
def index():
    return render_template("index.html")

with app.app_context(): 
    db.create_all()

if __name__ == "__main__":
    app.run(debug=True)
