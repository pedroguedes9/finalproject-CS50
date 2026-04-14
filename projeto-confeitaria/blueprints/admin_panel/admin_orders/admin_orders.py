from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import current_user, login_required
from sqlalchemy.orm import selectinload
from utils.pagination import paginate_query
from db import db
from models import  CartItems, OrderItems, Orders, Products
from decimal import Decimal

admin_orders_bp = Blueprint("admin_orders", __name__, template_folder="templates")