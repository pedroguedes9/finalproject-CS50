from flask import Blueprint, request, render_template, redirect, url_for
from flask_login import login_required
from db import db
from models import Products, Categories


products_bp = Blueprint("products", __name__, template_folder="templates")

@products_bp.route("/", methods = ["GET", "POST"])
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
        return redirect(url_for("products.products"))
    else:
        products = Products.query.all()
        categories = Categories.query.all()
        return render_template("products.html", products=products, categories=categories)

@products_bp.route("/delete", methods = ["POST"])
@login_required
def delete_product():
    product_id = request.form.get("id")
    product_id = int(product_id)
    product = Products.query.filter_by(id=product_id).first()
    db.session.delete(product)
    db.session.commit()
    return redirect(url_for('products.products'))

@products_bp.route("/categories", methods = ["POST"])
@login_required
def add_category():
    name = request.form.get("name")
    new_category = Categories(name=name)
    db.session.add(new_category)
    db.session.commit()
    return redirect(url_for('products.products'))
