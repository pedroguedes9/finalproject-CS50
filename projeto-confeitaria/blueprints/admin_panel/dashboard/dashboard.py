from flask import Blueprint, request, render_template, redirect, url_for, flash
from datetime import datetime, timedelta
from sqlalchemy import func
from models import Orders, Users, Products
from db import db

dashboard_bp = Blueprint('dashboard',__name__, template_folder="templates")

PERIODS = [7, 30, 60, 90]
STATUS_COLORS = {
    'recebido': 'bg-blue-50 text-blue-600 border border-blue-100',
    'preparando': 'bg-orange-50 text-orange-600 border border-orange-100',
    'pronto': 'bg-purple-50 text-purple-600 border border-purple-100',
    'saiu para entrega': 'bg-indigo-50 text-indigo-600 border border-indigo-100',
    'entregue': 'bg-green-50 text-green-600 border border-green-100',
}
PAYMENT_COLORS= {
    'pendente': 'bg-yellow-50 text-yellow-600 border border-yellow-100',
    'pago': 'bg-green-50 text-green-600 border border-green-100',
    'cancelado': 'bg-red-50 text-red-600 border border-red-100',
}

@dashboard_bp.route('/', methods=["GET", "POST"])
def dashboard():
    if request.method == "POST":
        period = request.form.get("period", str(PERIODS[1])).strip()
        return redirect(url_for('admin_panel.dashboard.dashboard', period=period))

    period = request.args.get("period", str(PERIODS[1]))

    try:
        period = int(period)
    except ValueError:
        flash("Período inválido", "error")
        return redirect(url_for('admin_panel.dashboard.dashboard'))
    if period not in PERIODS:
        flash("Período inválido", "error")
        return redirect(url_for('admin_panel.dashboard.dashboard'))
    period_date = datetime.now() - timedelta(days=period)
    period_before = datetime.now() - timedelta(days=period*2)

    orders_in_period = Orders.query.filter(Orders.created_at >= period_date).count()
    orders_in_period_before = Orders.query.filter(Orders.created_at.between(period_before, period_date)).count()
    if orders_in_period_before > 0:
        orders_in_period_variation = ((orders_in_period - orders_in_period_before) / orders_in_period_before) * 100   
    else: 
        orders_in_period_variation = orders_in_period * 100
    
    recent_orders = Orders.query.order_by(Orders.id.desc()).limit(5).all()

    total_invoicing = db.session.query(func.sum(Orders.total_price)).filter(Orders.created_at >= period_date).scalar() or 0
    total_invoicing_before = db.session.query(func.sum(Orders.total_price)).filter(Orders.created_at.between(period_before, period_date)).scalar() or 0
    if total_invoicing_before > 0:
        total_invoicing_variation = ((total_invoicing - total_invoicing_before) / total_invoicing_before) * 100
    else:
        total_invoicing_variation = total_invoicing * 100

    medium_ticket = 0
    if orders_in_period != 0:
        medium_ticket = total_invoicing / orders_in_period
    medium_ticket_before = 0
    if orders_in_period_before:
        medium_ticket_before = total_invoicing_before / orders_in_period_before
    if medium_ticket_before > 0:
        medium_ticket_variation = ((medium_ticket - medium_ticket_before) / medium_ticket_before) * 100
    else: 
        medium_ticket_variation = medium_ticket * 100

    new_users = Users.query.filter(Users.created_at >= period_date).count()
    new_users_before = Users.query.filter(Users.created_at.between(period_before, period_date)).count()
    if new_users_before > 0:
        new_users_variation = ((new_users - new_users_before) / new_users_before) * 100
    else:
        new_users_variation = new_users * 100

    unavailable_products = Products.query.filter_by(is_active=False).count()
    pendent_payments = Orders.query.filter_by(payment_status="pendente").count()
    low_stock_products = Products.query.filter(Products.stock < 2).count()

    return render_template(
        "dashboard.html", 
        periods=PERIODS,
        actual_period=period,
        orders_in_period=orders_in_period, 
        orders_in_period_variation=orders_in_period_variation, 
        recent_orders=recent_orders, 
        total_invoicing=total_invoicing, 
        total_invoicing_variation=total_invoicing_variation, 
        medium_ticket=medium_ticket, 
        medium_ticket_variation=medium_ticket_variation,
        new_users=new_users,
        new_users_variation=new_users_variation,
        unavailable_products=unavailable_products,
        pendent_payments=pendent_payments,
        low_stock_products=low_stock_products,
        status_colors=STATUS_COLORS,
        payment_colors=PAYMENT_COLORS
        )
