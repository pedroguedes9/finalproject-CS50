from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import current_user, login_required
from sqlalchemy.orm import selectinload
from utils.pagination import paginate_query
from db import db
from models import  CartItems, OrderItems, Orders, Products
from decimal import Decimal

orders_bp = Blueprint("orders", __name__, template_folder="templates")
@orders_bp.route("/checkout", methods=["POST"])
@login_required
def checkout():
    user_id = current_user.id
    user_cart_items = (
        CartItems.query
        .options(selectinload(CartItems.product))
        .filter_by(user_id=user_id).all()
    )

    if not user_cart_items:
        flash("Seu carrinho está vazio", "error")
        return redirect(url_for("cart.cart"))
    
    total_price = sum(Decimal(item.product.price) * Decimal(item.quantity) for item in user_cart_items)
    new_order = Orders(user_id=user_id, status="Recebido",payment_status="Pendente" ,total_price=total_price)
    db.session.add(new_order)
    db.session.flush()

    for item in user_cart_items:
        if item.product.stock < item.quantity:
            flash("Não há itens suficientes no estoque. Sua compra não foi finalizada", "error")
            db.session.rollback()
            return redirect(url_for("cart.cart"))
        
        item.product.stock = item.product.stock - item.quantity

        if item.product.is_active == False:
            flash("O produto que você está tentando comprar não está mais disponível. Sua compra não foi finalizada", "error")
            db.session.rollback()
            return redirect(url_for("cart.cart"))
        
        new_ordered_item = OrderItems(
            order_id=new_order.id,
            product_id=item.product_id,
            price=Decimal(item.product.price),
            quantity=item.quantity
        )
        db.session.add(new_ordered_item)
        db.session.delete(item)
    db.session.commit()
    return redirect(url_for("orders.orders"))

@orders_bp.route("/", methods=[ "GET"])
@login_required
def orders():
    user_id = current_user.id
    page = request.args.get("page", 1, type=int)
    per_page = 5

    base_query = (
        Orders.query
        .filter_by(user_id=user_id)
        .options(
            selectinload(Orders.items)
                .selectinload(OrderItems.product)
                .selectinload(Products.category)
        )
        .order_by(Orders.id.desc())
    )

    orders, total, total_pages, page = paginate_query(base_query, page, per_page)

    return render_template(
        "orders.html", 
        user_id=user_id, 
        orders=orders,
        page=page,
        total_pages=total_pages,
        per_page=per_page,
        total=total
    )
