from flask import Blueprint, request, render_template, redirect, url_for
from flask_login import login_required, current_user
from db import db
from models import Products, Categories


produtos_bp = Blueprint("produtos", __name__, template_folder="templates")

@produtos_bp.route("/products", methods = ["GET", "POST"])
@login_required
def products():
    if request.method == "POST":
        name = request.form.get("name")
        price = request.form.get("price")
        description = request.form.get("description")
        category_id = request.form.get("category-id")
        stock = request.form.get("stock")
        is_active = request.form.get("is-active")
        image = request.form.get("image")
        new_product = Products(name=name, price=price, description=description, category_id=category_id, stock=stock, is_active=is_active, image=image)
        db.session.add(new_product)
        db.session.commit()
        return redirect(url_for("produtos.products"))
    else:
        products = db.session.query(Products).all()
        categories = db.session.query(Categories).all()
        return render_template("products.html", products=products, categories=categories)

@produtos_bp.route("/del-product", methods = ["POST"])
@login_required
def del_product():
    if request.method == "POST":
        id = request.form.get("id")
        id = int(id)
        product = db.session.query(Products).filter_by(id=id).first()
        db.session.delete(product)
        db.session.commit()
        return redirect(url_for('produtos.products'))

@produtos_bp.route("/add-category", methods = ["POST"])
@login_required
def add_category():
    if request.method == "POST":
        name = request.form.get("name")
        new_category = Categories(name=name)
        db.session.add(new_category)
        db.session.commit()
        return redirect(url_for('produtos.products'))
