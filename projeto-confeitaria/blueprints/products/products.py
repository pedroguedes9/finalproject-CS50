import os
import uuid
from PIL import Image
from flask import Blueprint, request, render_template, redirect, url_for, flash
from flask_login import login_required
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import selectinload
from utils.decorators import admin_required
from utils.pagination import paginate_query
from db import db
from models import Products, Categories
from decimal import Decimal, InvalidOperation

products_bp = Blueprint("products", __name__, template_folder="templates")

@products_bp.route("/", methods = ["GET"])
def products():
    page = request.args.get("page", 1, type=int)
    per_page = 12

    base_query = products = (
        Products.query
        .options(selectinload(Products.category))
        .order_by(Products.is_active.desc(), Products.id.asc())
    )
    products, total, total_pages, page = paginate_query(base_query, page, per_page)
    
    return render_template(
        "products.html", 
        products=products,
        page=page,
        total_pages=total_pages
    )




