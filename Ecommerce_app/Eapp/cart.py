from flask import Flask, url_for, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy 

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:sfdc123*@localhost:5432/flask_db'
app.config['SECRET_KEY'] = 'secret'
db = SQLAlchemy(app)


class Cart(db.Model):
    __tablename__ = "cart"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    item_name = db.Column(db.String(5000), nullable=False)
    price = db.Column(db.String(5000), nullable=False)


with app.app_context():
    db.create_all()
