from flask import Blueprint, request, render_template, redirect, url_for, flash     
from flask_login import current_user, login_required
from db import db
from models import  CartItems, OrderItems, Orders
from decimal import Decimal

orders_bp = Blueprint("orders", __name__, template_folder="templates")
@orders_bp.route("/checkout", methods=["POST"])
@login_required
def checkout():
    user_id = current_user.id
    user_cart_items = CartItems.query.filter_by(user_id=user_id).all()

    if not user_cart_items:
        flash("Seu carrinho está vazio", "warning")
        return redirect(url_for("cart.cart"))
    
    total_price = sum(Decimal(item.product.price) * Decimal(item.quantity) for item in user_cart_items)
    new_order = Orders(user_id=user_id, status="pending", total_price=total_price)
    db.session.add(new_order)
    db.session.flush()

    for item in user_cart_items:
        if item.product.stock < item.quantity:
            flash("Não há itens suficientes no estoque. Sua compra não foi finalizada", "warning")
            db.session.rollback()
            return redirect(url_for("cart.cart"))

        if not item.product.is_active:
            flash("O produto que você está tentando comprar não está mais disponível. Sua compra não foi finalizada", "warning")
            db.session.rollback()
            return redirect(url_for("cart.cart"))
        
        item.product.stock = item.product.stock - item.quantity
        if item.product.stock == 0:
            item.product.is_active = False
        new_ordered_item = OrderItems(
            order_id=new_order.id,
            product_id=item.product_id,
            price=Decimal(item.product.price),
            quantity=item.quantity
        )
        db.session.add(new_ordered_item)
        db.session.delete(item)
    db.session.commit()
    flash("Compra realizada com sucesso", "success")
    return redirect(url_for("cart.cart"))

@orders_bp.route("/", methods=[ "GET"])
@login_required
def orders():
    user_id = current_user.id
    orders = current_user.orders
    return render_template("orders.html", user_id=user_id, orders=orders)
