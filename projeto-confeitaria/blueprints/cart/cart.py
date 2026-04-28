from flask import Blueprint, request, render_template, redirect, url_for, flash
from db import db
from sqlalchemy.orm import selectinload
from sqlalchemy.exc import IntegrityError
from utils.pagination import paginate_query
from flask_login import current_user, login_required
from models import  CartItems, Products
from decimal import Decimal

cart_bp = Blueprint("cart", __name__, template_folder="templates")

@cart_bp.route("/add", methods=["POST"])
@login_required
def add_to_cart():
    user_id = current_user.id
    product_id = request.form.get("id")
    quantity = request.form.get("quantity")
    if not product_id:
        flash("Por favor, adicione um produto que esteja disponível.", "error")
        return redirect(url_for('products.products'))
    if not quantity:
        flash("Por favor, insira uma quantidade", "error")
        return redirect(url_for('products.products'))
    
    try:
        product_id = int(product_id)
    except ValueError:
        flash("Por favor, o id do produto deve ser um número válido", "error")
        return redirect(url_for('products.products'))

    try:
        quantity = int(quantity)
    except ValueError:
        flash("Por favor, a quantidade deve ser um número", "error")
        return redirect(url_for('products.products'))
    if quantity < 1:
        flash("Por favor, a quantidade deve ser um numero maior que 0", "error")
        return redirect(url_for('products.products'))

    product = Products.query.filter_by(id=product_id).first()
    if not product:
        flash("O produto escolhido não existe", "error")
        return redirect(url_for('products.products'))
    if product.stock < 1 or product.is_active == False:
        flash("O produto não está mais disponível", "error")
        return redirect(url_for('products.products'))
    
    existing_item = CartItems.query.filter_by(user_id=user_id, product_id=product_id).first()
    if existing_item:
        new_quantity = existing_item.quantity + quantity
        if new_quantity > product.stock:
            flash("Quantidade total excede o estoque disponível","error")
            return redirect(url_for('cart.cart'))
        else:
            existing_item.quantity = new_quantity
    else:
        if quantity > product.stock:
            flash("Quantidade total excede o estoque disponível", "error")
            return redirect(url_for('cart.cart'))
        new_cart_item = CartItems(user_id=user_id, product_id=product_id, quantity=quantity)
        db.session.add(new_cart_item)
    db.session.commit()
    return redirect(url_for("cart.cart"))

@cart_bp.route("/", methods=["GET"])
@login_required
def cart():
    user_id = current_user.id
    page = request.args.get("page", 1, type=int)
    per_page = 6

    base_query = (
        CartItems.query
        .filter_by(user_id=user_id)
        .options(
            selectinload(CartItems.product)
                .selectinload(Products.category)
        )
    )
    cart_items, total, total_pages, page = paginate_query(base_query, page, per_page)

    all_items = (
        CartItems.query
        .filter_by(user_id=user_id)
        .options(selectinload(CartItems.product))
        .all()
    )
    total_price = sum(Decimal(item.product.price) * Decimal(item.quantity) for item in cart_items)

    return render_template(
        "cart.html", 
        cart_items = cart_items, 
        user_id=user_id, 
        total_price=total_price,
        page=page,
        total_pages=total_pages,
    )


@cart_bp.route("/remove", methods=["POST"])
@login_required
def remove_from_cart():
    user_id = current_user.id
    item_id = request.form.get("id")
    
    if item_id == "":
        flash("Id do produto não foi fornecido", "error")
        return redirect(url_for('.cart'))
    
    try:
        item_id = int(item_id)
    except ValueError:
        flash("O id do item tem que ser um número")
        return redirect(url_for('.cart'))
    if item_id < 1:
        flash("O id do item tem que ser maior que 0")
        return redirect(url_for('.cart'))
    
    item = CartItems.query.filter_by(id=item_id, user_id=user_id).first()
    if not item:
        flash("O item que você tentou remover não existe", "error")
        return redirect(url_for('.cart'))
    
    db.session.delete(item)
    db.session.commit()
    return redirect(url_for('.cart'))


@cart_bp.route("/decrease", methods=["POST"])
@login_required
def decrease_quantity():
    user_id = current_user.id
    item_id = request.form.get("id", "")
    if item_id == "":
        flash("Id do produto não foi fornecido", "error")
        return redirect(url_for('.cart'))

    try:
        item_id = int(item_id)
    except ValueError:
        flash("Id de produto inválido", "error")
        return redirect(url_for('.cart'))

    if item_id < 1:
        flash("Id de produto inválido", "error")
        return redirect(url_for('.cart'))

    item = CartItems.query.filter_by(id=item_id, user_id=user_id).first()
    if not item:
        flash("Esse produto não existe ou não está no seu carrinho", "error")
        return redirect(url_for('.cart'))

    quantity = request.form.get("quantity", "")
    if quantity == "":
        flash("A quantidade que quer remover do carrinho não foi fornecida", "error")
        return redirect(url_for('.cart'))
    
    try:
        quantity = int(quantity)
    except ValueError:
        flash("A quantidade fornecida é inválida", "error")
        return redirect(url_for('.cart'))
    
    if quantity < 1 or quantity > 1:
        flash("A quantidade fornecida é inválida", "error")
        return redirect(url_for('.cart'))
    
    if item.quantity > 1:
        item.quantity = item.quantity - quantity
    elif item.quantity == 1:
        db.session.delete(item)
    else:
        flash("A quantidade do produto no carrinho é inválida","error")
        return redirect(url_for('.cart'))
    
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        flash("Não foi possível efetuar as mudanças. Tente novamente mais tarde.", "error")
        return redirect(url_for('.cart'))
    return redirect(url_for('.cart'))