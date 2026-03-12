from flask import Flask, render_template, request, redirect, url_for
from db import db
from models import Users, Products, CartItems, OrderItems, Orders, Categories

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///confeitaria.db"
db.init_app(app)


@app.route("/",methods = ["GET", "POST"])
def index():
    if request.method == "POST":
        username = request.form.get("username")
        email = request.form.get("email")
        password = request.form.get("password")
        telefone = request.form.get("telefone")
        new_user = Users(username=username, email=email, password=password, telefone_number=telefone)
        db.session.add(new_user)
        db.session.commit()
        return redirect("/")
    else:
        users = db.session.query(Users).all()
        return render_template("index.html", users=users)

@app.route("/delete", methods = ["POST"])
def delete():
    if request.method == "POST":
        id = request.form.get("id")
        user = db.session.query(Users).filter_by(id=id).first()
        db.session.delete(user)
        db.session.commit()
        return redirect("/")

@app.route("/change", methods = ["POST"])
def change():
    if request.method == "POST":
        id = request.form.get("id")
        new_name = request.form.get("new_name")
        user = db.session.query(Users).filter_by(id=id).first()
        user.username = new_name
        db.session.commit()
        return redirect("/")

@app.route("/products", methods = ["GET", "POST"])
def products():
    if request.method == "POST":
        name = request.form.get("name")
        price = request.form.get("price")
        description = request.form.get("description")
        category_id = request.form.get("category-id")
        stock = request.form.get("stock")
        is_active = request.form.get("is-active")
        image = request.form.get("image")
        new_product = Products(name=name, price=price, description=description, category_id=category_id, stock=stock, is_active=is_active, image=image)
        db.session.add(new_product)
        db.session.commit()
        return redirect(url_for("products"))
    else:
        products = db.session.query(Products).all()
        categories = db.session.query(Categories).all()
        return render_template("products.html", products=products, categories=categories)

@app.route("/del-product", methods = ["POST"])
def del_product():
    if request.method == "POST":
        id = request.form.get("id")
        id = int(id)
        product = db.session.query(Products).filter_by(id=id).first()
        db.session.delete(product)
        db.session.commit()
        return redirect(url_for('products'))

@app.route("/add-category", methods = ["POST"])
def add_category():
    if request.method == "POST":
        name = request.form.get("name")
        new_category = Categories(name=name)
        db.session.add(new_category)
        db.session.commit()
        return redirect(url_for('products'))

@app.route("/add-to-cart", methods=["POST"])
def add_to_cart():
    if request.method == "POST":
        product_id = request.form.get("id")
        user_id = 4
        quantity = 1
        new_cart_item = CartItems(user_id=user_id, product_id=product_id, quantity=quantity)
        db.session.add(new_cart_item)
        db.session.commit()
        return redirect(url_for("products"))

@app.route("/cart", methods=["GET", "POST"])
def cart():
    if request.method == "POST":
        id = request.form.get("id")
        id = int(id)
        cart_items = db.session.query(CartItems).filter_by(user_id = id).all()
        total_price = sum(int(item.product.price) * int(item.quantity) for item in cart_items)
        return render_template("cart.html", cart_items = cart_items, user_id=id, total_price=total_price)
    else:
        return render_template("cart.html", cart_items = None)

@app.route("/del-from-cart", methods=["POST"])
def del_from_cart():
    if request.method == "POST":
        item_id = request.form.get("id")
        item_id = int(item_id)
        item = db.session.query(CartItems).filter_by(id=item_id).first()
        db.session.delete(item)
        db.session.commit()

        id = request.form.get("user-id")
        id = int(id)
        cart_items = db.session.query(CartItems).filter_by(user_id = id).all()
        return render_template("cart.html", cart_items = cart_items, user_id=id)

@app.route("/buy", methods=["POST"])
def buy():
    if request.method == "POST":
        user_id = request.form.get("user-id")
        user_id = int(user_id)
        user_cart = db.session.query(CartItems).filter_by(user_id=user_id)

        total_price = sum(int(item.product.price) * int(item.quantity) for item in user_cart)
        new_order = Orders(user_id=user_id, status="pendente", total_price=total_price)
        db.session.add(new_order)
        db.session.commit()

        for item in user_cart:
            new_ordered_item = OrderItems(
                order_id=new_order.id,
                product_id=item.product_id,
                price=int(item.product.price),
                quantity=item.quantity
            )
            db.session.add(new_ordered_item)
            db.session.delete(item)
        db.session.commit()
        return redirect(url_for("cart"))

@app.route("/orders", methods=["POST", "GET"])
def orders():
    if request.method == "POST":
        user_id = request.form.get("user-id")
        user_id = int(user_id)
        orders = db.session.query(Orders).filter_by(user_id=user_id).all()

        return render_template("orders.html", user_id=user_id, orders=orders)
    else:
        return render_template("orders.html")
with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run(debug=True)
