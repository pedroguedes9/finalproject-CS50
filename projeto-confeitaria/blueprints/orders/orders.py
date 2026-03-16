from flask import Blueprint, request, render_template, redirect, url_for
from flask_login import current_user, login_required
from db import db
from models import  CartItems, OrderItems, Orders

orders_bp = Blueprint("orders", __name__, template_folder="templates")
@orders_bp.route("/checkout", methods=["POST"])
@login_required
def checkout():
    user_id = current_user.id
    user_cart_items = CartItems.query.filter_by(user_id=user_id)
    total_price = sum(float(item.product.price) * int(item.quantity) for item in user_cart_items)
    new_order = Orders(user_id=user_id, status="pending", total_price=total_price)
    db.session.add(new_order)
    db.session.commit()

    for item in user_cart_items:
        new_ordered_item = OrderItems(
            order_id=new_order.id,
            product_id=item.product_id,
            price=float(item.product.price),
            quantity=item.quantity
        )
        db.session.add(new_ordered_item)
        db.session.delete(item)
    db.session.commit()
    return redirect(url_for("cart.cart"))

@orders_bp.route("/", methods=[ "GET"])
@login_required
def orders():
    user_id = current_user.id
    orders = Orders.query.filter_by(user_id=user_id).all()
    return render_template("orders.html", user_id=user_id, orders=orders)
