from db import db
from sqlalchemy import func

class Users(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(30), nullable=False, unique=True )
    email = db.Column(db.String(100), nullable=False, unique=True)
    password = db.Column(db.String(255), nullable=False) #255 para senha pois usa um hash
    telefone_number = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=func.now())

    cart_items = db.relationship("CartItems", backref="user")
    orders = db.relationship("Orders", backref="user")

    def __init__(self, username:str, email:str, password:str, telefone_number:int):
        self.username = username
        self.email = email
        self.password = password
        self.telefone_number = telefone_number


class Products(db.Model):
    __tablename__ = "products"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), nullable=False)
    price = db.Column(db.Numeric(10, 2), nullable=False)
    description = db.Column(db.String, nullable=True)
    category_id = db.Column(db.Integer, db.ForeignKey("categories.id"), nullable=True)
    stock = db.Column(db.Integer, nullable=True)
    is_active = db.Column(db.Integer, nullable=False, default=1)
    image = db.Column(db.String, nullable=True)
    created_at = db.Column(db.DateTime, default=func.now())

    order_items = db.relationship("OrderItems", backref="product")

    def __init__(self, name:str, price:float, description:str | None, category_id:int | None, stock:int, image:str | None, is_active:int ):
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
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey("products.id"), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=func.now())

    product = db.relationship("Products", backref="cart_items")

    def __init__(self,user_id:int, product_id:int, quantity:int):
        self.user_id = user_id
        self.product_id = product_id
        self.quantity = quantity

    def __repr__(self):
        return f"<CartItems user_id={self.user_id} product_id={self.product_id} quantity={self.quantity}>"


class Orders(db.Model):
    __tablename__ = "orders"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    status = db.Column(db.String(30) ,nullable=False)
    total_price = db.Column(db.Numeric(10, 2), nullable=False)
    created_at = db.Column(db.DateTime, default=func.now())

    items = db.relationship("OrderItems", backref="order")

    def __init__(self, user_id:int, status:str, total_price:float ):
        self.user_id = user_id
        self.status = status
        self.total_price = total_price

class OrderItems(db.Model):
    __tablename__ = "order_items"

    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey("orders.id"), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey("products.id"), nullable=False)
    price = db.Column(db.Numeric(10, 2), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)

    def __init__(self, order_id: int, product_id:int, price:float, quantity:int):
        self.order_id =order_id
        self.product_id = product_id
        self.price = price
        self.quantity = quantity