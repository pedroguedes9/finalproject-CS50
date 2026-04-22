from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import current_user, login_required
from sqlalchemy.orm import selectinload
from sqlalchemy.exc import IntegrityError
from utils.pagination import paginate_query
from db import db
from models import  CartItems, OrderItems, Orders, Products, OrderStatus,PaymentStatus ,Categories
from decimal import Decimal, InvalidOperation

admin_orders_bp = Blueprint("admin_orders", __name__, template_folder="templates")

@admin_orders_bp.route("/", methods=["GET"])
def orders():
    user_id = current_user.id
    page = request.args.get("page", 1, type=int)
    per_page = 5

    base_query = (
        Orders.query
        .options(
            selectinload(Orders.items)
                .selectinload(OrderItems.product)
                .selectinload(Products.category)
        )
        .order_by(Orders.id.desc())
    )

    status = request.args.get("status", "").strip()
    if status != "":
        valid_values = [s.value for s in OrderStatus]
        if status not in valid_values:
            flash("Por favor, insira um status válido para filtrar", "error")
            return redirect(url_for('admin_panel.admin_orders.orders'))
        
        base_query = base_query.filter(Orders.status==status)

    payment_status = request.args.get("payment-status", "").strip()
    if payment_status != "":
        valid_statuses = [e.value for e in PaymentStatus]
        if payment_status not in valid_statuses:
            flash("Por favor, insira um status válido para filtrar", "error")
            return redirect(url_for('admin_panel.admin_orders.orders'))
        
        base_query = base_query.filter(Orders.payment_status==payment_status)

    min_price_str = request.args.get("min-price", "").strip()
    max_price_str = request.args.get("max-price", "").strip()

    min_price_val = None
    max_price_val = None

    if min_price_str != "":
        try:
            min_price_val =  Decimal(min_price_str)
        except InvalidOperation:
            flash("Preço mínimo inválido", "error")
            return redirect(url_for('admin_panel.admin_orders.orders'))
        if min_price_val < 0:
            flash("Preço mínimo inválido", "error")
            return redirect(url_for('admin_panel.admin_orders.orders'))
    
    if max_price_str != "":
        try:
            max_price_val = Decimal(max_price_str)
        except InvalidOperation:
            flash("Preço máximo inválido", "error")
            return redirect(url_for('admin_panel.admin_orders.orders'))
        if max_price_val < 0:
            flash("Preço máximo inválido", "error")
            return redirect(url_for('admin_panel.admin_orders.orders'))

    if min_price_val != None and max_price_val != None:
        if min_price_val > max_price_val:
            flash("O mínimo não pode ser maior que o máximo", "error")
            return redirect(url_for('admin_panel.admin_orders.orders'))

    if min_price_val != None:
        base_query = base_query.filter(Orders.total_price >= min_price_val)
    if max_price_val != None:
        base_query = base_query.filter(Orders.total_price <= max_price_val)


    product_name = request.args.get("product-name", "").strip().lower()
    if product_name != "":
        base_query = base_query.filter(
            # onde a lista de "items" possua qualquer (.any) item...
            Orders.items.any(
                # ... que "tenha" (.has) um produto...
                OrderItems.product.has(
                    # ... cujo nome seja parecido com o pesquisado.
                    Products.name.ilike(f"%{product_name}%")
                )
            )
        )


    category_name = request.args.get("category-name", "").strip().lower()
    if category_name != "":
        base_query = base_query.filter(
            # onde a lista de "items" possua qualquer (.any) item...
            Orders.items.any(
                # ... que "tenha" (.has) um produto...
                OrderItems.product.has(
                    # ... cujo o produto tenha uma categoria com...
                    Products.category.has(
                        # ... o nome parecido com o fornecido
                        Categories.name.ilike(f"%{category_name}%")
                    )
                )
            )
        )

    categories = Categories.query.all()

    orders, total, total_pages, page = paginate_query(base_query, page, per_page)

    return render_template(
        "admin_orders.html",
        user_id=user_id,
        orders=orders,
        page=page,
        total_pages=total_pages,
        per_page=per_page,
        total=total,
        OrderStatus=OrderStatus,
        PaymentStatus=PaymentStatus,
        payment_current_status=payment_status,
        current_status=status,
        min_price_val=min_price_val,
        max_price_val=max_price_val,
        product_name=product_name,
        categories=categories,
        current_category_name=category_name,
        category_name=category_name
    )


@admin_orders_bp.route("/edit", methods=["POST"])
def edit_order():
    if request.method == "POST":
        order_id = request.form.get("id", "").strip()

        if order_id == "":
            flash("Id do pedido que deseja editar não foi fornecido", "error")
            return redirect(url_for('.orders'))
        try:
            order_id = int(order_id)
        except ValueError: 
            flash("Id inválido", "error")
            return redirect(url_for('.orders'))
        if order_id < 1:
            flash("Id inválido", "error")
            return redirect(url_for('.orders'))
        
        order = Orders.query.filter_by(id=order_id).first()
        if not order:
            flash("Id inválido", "error")
            return redirect(url_for('.orders'))

        changed = False

        status = request.form.get("status","").strip()
        if status != "":
            valid_statuses = [e.value for e in OrderStatus]
            if status in valid_statuses:
                if order.status.value != status:
                    order.status = status
                    changed = True
        
        payment_status = request.form.get("payment_status","").strip()
        if payment_status != "":
            valid_payment_statuses = [e.value for e in PaymentStatus]
            if payment_status in valid_payment_statuses:
                if order.payment_status.value != payment_status:
                    order.payment_status = payment_status
                    changed = True

        return_url = request.form.get("url", url_for('.orders'))

        if not changed:
            flash("Nenhuma alteração foi feita", "info")
            return redirect(return_url)

        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            flash("Não foi possível efetuar as mudanças. Tente novamente mais tarde.", "error")
            return redirect(url_for('.orders'))
        
        flash("Edição concluída com sucesso", "success")
        return redirect(return_url)