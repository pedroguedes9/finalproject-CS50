import os
from flask import Flask, render_template
from flask_login import LoginManager
from db import db
from models import Users
from blueprints.cart.cart import cart_bp
from blueprints.products.products import products_bp
from blueprints.orders.orders import orders_bp
from blueprints.auth.auth import auth_bp
from dotenv import load_dotenv


load_dotenv()


app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///confeitaria.db"

db.init_app(app)

login_manager = LoginManager(app)
login_manager.login_view = 'auth.login'

app.register_blueprint(products_bp, url_prefix="/products")
app.register_blueprint(cart_bp, url_prefix="/cart")
app.register_blueprint(orders_bp, url_prefix="/orders")
app.register_blueprint(auth_bp, url_prefix="/auth")



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
