from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from db import db


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///confeitaria.db"
db = SQLAlchemy()
db.init_app(app)


@app.route("/")
def index():
    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)