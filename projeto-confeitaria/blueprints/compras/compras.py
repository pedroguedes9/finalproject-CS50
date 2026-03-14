from flask import Blueprint, request, render_template, redirect, url_for
from flask_login import current_user, login_required
from db import db
from models import  CartItems, OrderItems, Orders

compras_bp = Blueprint("compras", __name__, template_folder="templates")
@compras_bp.route("/buy", methods=["POST"])
@login_required
def buy():
    if request.method == "POST":
        user_id = current_user.id
        user_cart = db.session.query(CartItems).filter_by(user_id=user_id)

        total_price = sum(int(item.product.price) * int(item.quantity) for item in user_cart)
        new_order = Orders(user_id=user_id, status="pendente", total_price=total_price)
        db.session.add(new_order)
        db.session.commit()

        for item in user_cart:
            new_ordered_item = OrderItems(
                order_id=new_order.id,
                product_id=item.product_id,
                price=int(item.product.price),
                quantity=item.quantity
            )
            db.session.add(new_ordered_item)
            db.session.delete(item)
        db.session.commit()
        return redirect(url_for("carrinho.cart"))

@compras_bp.route("/orders", methods=[ "GET"])
@login_required
def orders():
    user_id = current_user.id
    orders = db.session.query(Orders).filter_by(user_id=user_id).all()
    return render_template("orders.html", user_id=user_id, orders=orders)
