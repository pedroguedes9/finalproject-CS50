from flask import Blueprint, request, render_template, redirect, url_for, flash
from db import db
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
            return redirect(url_for('products.products'))
        else:
            existing_item.quantity = new_quantity
    else:
        if quantity > product.stock:
            flash("Quantidade total excede o estoque disponível", "error")
            return redirect(url_for('products.products'))
        new_cart_item = CartItems(user_id=user_id, product_id=product_id, quantity=quantity)
        db.session.add(new_cart_item)
    db.session.commit()
    flash("Item adicionado ao carrinho!", "success")
    return redirect(url_for("products.products"))

@cart_bp.route("/", methods=["GET"])
@login_required
def cart():
    user_id = current_user.id
    cart_items = current_user.cart_items
    total_price = sum(Decimal(item.product.price) * Decimal(item.quantity) for item in cart_items)
    return render_template("cart.html", cart_items = cart_items, user_id=user_id, total_price=total_price)


@cart_bp.route("/remove", methods=["POST"])
@login_required
def remove_from_cart():
    user_id = current_user.id
    item_id = request.form.get("id")
    
    try:
        item_id = int(item_id)
    except ValueError:
        flash("O id do item tem que ser um número", "error")
        return redirect(url_for('cart.cart'))
    if item_id < 1:
        flash("O id do item tem que ser maior que 0", "error")
        return redirect(url_for('cart.cart'))
    
    item = CartItems.query.filter_by(id=item_id, user_id=user_id).first()
    if not item:
        flash("O item que você tentou remover não existe", "error")
        return redirect(url_for('cart.cart'))
    
    db.session.delete(item)
    db.session.commit()
    flash("Item removido do carrinho.", "success")
    return redirect(url_for('cart.cart'))
