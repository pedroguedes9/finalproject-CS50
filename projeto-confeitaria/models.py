from db import db
from flask_login import UserMixin
from sqlalchemy import func
from decimal import Decimal
import enum

class Users(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(30), nullable=False )
    email = db.Column(db.String(100), nullable=False, unique=True)
    password = db.Column(db.String, nullable=False) #255 para senha pois usa um hash
    phone_number = db.Column(db.String(15), nullable=False)
    is_admin = db.Column(db.Boolean, nullable=False, default=False)
    created_at = db.Column(db.DateTime, default=func.now())

    cart_items = db.relationship("CartItems", backref="user")
    orders = db.relationship("Orders", backref="user")

    def __init__(self, username:str, email:str, password:str, phone_number:str):
        self.username = username
        self.email = email
        self.password = password
        self.phone_number = phone_number


class Products(db.Model):
    __tablename__ = "products"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), nullable=False)
    price = db.Column(db.Numeric(10, 2), nullable=False)
    description = db.Column(db.String, nullable=True)
    category_id = db.Column(db.Integer, db.ForeignKey("categories.id"), nullable=True, index=True)
    stock = db.Column(db.Integer, nullable=False)
    is_active = db.Column(db.Boolean, nullable=False, default=1)
    image = db.Column(db.String, nullable=True)
    created_at = db.Column(db.DateTime, default=func.now())

    order_items = db.relationship("OrderItems", backref="product")

    def __init__(self, name:str, price:Decimal, description:str | None, category_id:int | None, stock:int, image:str | None, is_active:int ):
        self.name = name
        self.price = price
        self.description = description
        self.category_id = category_id
        self.stock = stock
        self.is_active = is_active
        self.image = image

class Categories(db.Model):
    __tablename__ = "categories"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), nullable=False, unique=True)

    products = db.relationship("Products", backref="category")

    def __init__(self, name:str):
        self.name = name

class CartItems(db.Model):
    __tablename__ = "cart_items"
    __table_args__ = (db.UniqueConstraint("user_id", "product_id"),)

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    product_id = db.Column(db.Integer, db.ForeignKey("products.id"), nullable=False, index=True)
    quantity = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=func.now())

    product = db.relationship("Products", backref="cart_items")
    
    def __init__(self,user_id:int, product_id:int, quantity:int):
        self.user_id = user_id
        self.product_id = product_id
        self.quantity = quantity

    def __repr__(self):
        return f"<CartItems user_id={self.user_id} product_id={self.product_id} quantity={self.quantity}>"


class OrderStatus(enum.Enum):
    RECEBIDO = "Recebido"
    PREPARANDO = "Preparando"
    PRONTO = "Pronto"
    SAIU_PARA_ENTREGA = "Saiu para entrega"
    ENTREGUE = "Entregue"

class PaymentStatus(enum.Enum):
    PENDENT = "Pendente"
    PAYED = "Pago"
    CANCELED = "Cancelado"
class Orders(db.Model):
    __tablename__ = "orders"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    status = db.Column(db.Enum(OrderStatus, values_callable=lambda x:[e.value for e in x]) ,nullable=False)
    payment_status = db.Column(db.Enum(PaymentStatus, values_callable=lambda x:[e.value for e in x]) ,nullable=False, default=PaymentStatus.PENDENT.value)
    # Usei o 'values_callable' para forçar o SQLAlchemy a gravar e ler o 'value' do Enum (lado direito, ex: "Pendente") 
    # no banco de dados, ignorando o name/chave (lado esquerdo, ex: "PENDENT"). Isso evita o erro de LookupError.
    total_price = db.Column(db.Numeric(10, 2), nullable=False)
    created_at = db.Column(db.DateTime, default=func.now())

    items = db.relationship("OrderItems", backref="order")

    def __init__(self, user_id:int, status:str, payment_status:str ,total_price:Decimal ):
        self.user_id = user_id
        self.status = status
        self.total_price = total_price
        self.payment_status = payment_status


class OrderItems(db.Model):
    __tablename__ = "order_items"

    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey("orders.id"), nullable=False, index=True)
    product_id = db.Column(db.Integer, db.ForeignKey("products.id"), nullable=False, index=True)
    price = db.Column(db.Numeric(10, 2), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)

    def __init__(self, order_id: int, product_id:int, price:Decimal, quantity:int):
        self.order_id =order_id
        self.product_id = product_id
        self.price = price
        self.quantity = quantity