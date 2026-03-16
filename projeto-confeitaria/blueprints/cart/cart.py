from flask import Blueprint, request, render_template, redirect, url_for
from db import db
from flask_login import current_user, login_required
from models import  CartItems

cart_bp = Blueprint("cart", __name__, template_folder="templates")

@cart_bp.route("/add", methods=["POST"])
@login_required
def add_to_cart():
    product_id = request.form.get("id")
    user_id = current_user.id
    quantity = 1
    new_cart_item = CartItems(user_id=user_id, product_id=product_id, quantity=quantity)
    db.session.add(new_cart_item)
    db.session.commit()
    return redirect(url_for("products.products"))

@cart_bp.route("/", methods=["GET"])
@login_required
def cart():
    user_id = current_user.id
    cart_items = CartItems.query.filter_by(user_id=user_id).all()
    total_price = sum(float(item.product.price) * int(item.quantity) for item in cart_items)
    return render_template("cart.html", cart_items = cart_items, user_id=user_id, total_price=total_price)


@cart_bp.route("/remove", methods=["POST"])
@login_required
def remove_from_cart():
    item_id = request.form.get("id")
    item_id = int(item_id)
    item = CartItems.query.filter_by(id=item_id).first()
    db.session.delete(item)
    db.session.commit()
    return redirect(url_for('cart.cart'))
