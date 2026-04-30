from flask import Blueprint, request, render_template, redirect, url_for, flash
from sqlalchemy.orm import selectinload
from utils.pagination import paginate_query
from models import Products, Categories
from decimal import Decimal, InvalidOperation

products_bp = Blueprint("products", __name__, template_folder="templates")

@products_bp.route("/", methods = ["GET"])
def products():
    page = request.args.get("page", 1, type=int)
    per_page = 12

    base_query = (
        Products.query
        .options(selectinload(Products.category))
        .order_by(Products.is_active.desc(), Products.id.asc())
    )

    min_price_str = request.args.get("min-price", "").strip()
    max_price_str = request.args.get("max-price", "").strip()

    min_price_val = None
    max_price_val = None

    if min_price_str != "":
        try:
            min_price_val = Decimal(min_price_str)
        except InvalidOperation:
            flash("Preço mínimo inválido", "error")
            return redirect(url_for('products.products'))
        if min_price_val < 0:
            flash("Preço mínimo inválido", "error")
            return redirect(url_for('products.products'))

    if max_price_str != "":
        try:
            max_price_val = Decimal(max_price_str)
        except InvalidOperation:
            flash("Preço máximo inválido", "error")
            return redirect(url_for('products.products'))
        if max_price_val < 0:
            flash("Preço máximo inválido", "error")
            return redirect(url_for('products.products'))

    if min_price_val is not None and max_price_val is not None and min_price_val > max_price_val:
        flash("O mínimo não pode ser maior que o máximo", "error")
        return redirect(url_for('products.products'))

    if min_price_val is not None:
        base_query = base_query.filter(Products.price >= min_price_val)
    if max_price_val is not None:
        base_query = base_query.filter(Products.price <= max_price_val)

    product_name = request.args.get("product-name", "").strip()
    if product_name != "":
        base_query = base_query.filter(
            Products.name.ilike(f"%{product_name}%")
        )

    current_category_name = request.args.get("category-name", "").strip()
    if current_category_name != "":
        base_query = base_query.filter(
            Products.category.has(
                Categories.name.ilike(f"%{current_category_name}%")
            )
        )

    products, total, total_pages, page = paginate_query(base_query, page, per_page)
    categories = Categories.query.all()
    
    return render_template(
        "products.html", 
        products=products,
        page=page,
        total_pages=total_pages,
        categories=categories,
        min_price_val=min_price_val,
        max_price_val=max_price_val,
        product_name=product_name,
        current_category_name=current_category_name
    )




