from flask import Blueprint, request, render_template, redirect, url_for
from db import db
from flask_login import current_user, login_required
from models import  CartItems

carrinho_bp = Blueprint("carrinho", __name__, template_folder="templates")

@carrinho_bp.route("/add-to-cart", methods=["POST"])
@login_required
def add_to_cart():
    if request.method == "POST":
        product_id = request.form.get("id")
        user_id = current_user.id
        quantity = 1
        new_cart_item = CartItems(user_id=user_id, product_id=product_id, quantity=quantity)
        db.session.add(new_cart_item)
        db.session.commit()
        return redirect(url_for("produtos.products"))

@carrinho_bp.route("/cart", methods=["GET"])
@login_required
def cart():
    user_id = current_user.id
    cart_items = db.session.query(CartItems).filter_by(user_id = user_id).all()
    total_price = sum(int(item.product.price) * int(item.quantity) for item in cart_items)
    return render_template("cart.html", cart_items = cart_items, user_id=user_id, total_price=total_price)


@carrinho_bp.route("/del-from-cart", methods=["POST"])
@login_required
def del_from_cart():
    if request.method == "POST":
        item_id = request.form.get("id")
        item_id = int(item_id)
        item = db.session.query(CartItems).filter_by(id=item_id).first()
        db.session.delete(item)
        db.session.commit()

        user_id = current_user.id
        cart_items = db.session.query(CartItems).filter_by(user_id = user_id).all()
        return render_template("cart.html", cart_items = cart_items, user_id=user_id)
