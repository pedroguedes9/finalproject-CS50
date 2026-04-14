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

admin_products_bp = Blueprint("admin_products", __name__, template_folder="templates")