from flask import Flask, render_template, request, redirect
from db import db
from models import Users

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

@app.route("/delete", methods = ["GET", "POST"])
def delete():
    if request.method == "POST":
        id = request.form.get("id")
        user = db.session.query(Users).filter_by(id=id).first()
        db.session.delete(user)
        db.session.commit()
        return redirect("/")

@app.route("/change", methods = ["GET", "POST"])
def change():
    if request.method == "POST":
        id = request.form.get("id")
        new_name = request.form.get("new_name")
        user = db.session.query(Users).filter_by(id=id).first()
        user.username = new_name
        db.session.commit()
        return redirect("/")

with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run(debug=True)
