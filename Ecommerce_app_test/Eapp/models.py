from sqlalchemy import func
from . import db
from flask_login import UserMixin
from datetime import datetime


class Eapp(db.Model, UserMixin):
    __tablename__ = "eapp"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.String(5000), nullable=False, unique=True)
    password = db.Column(db.String(5000), nullable=False)
    name = db.Column(db.String(100))
    gender = db.Column(db.String(20))

    # cart_items = db.relationship('Cart', backref=db.backref('eapp', lazy=True))
    # orders = db.relationship('Order', backref=db.backref('eapp', lazy=True))

    def __repr__(self):
        return f"({self.id}) {self.name},{self.gender} - {self.email} -- {self.password}"

class Product(db.Model):
    sno = db.Column(db.Integer, autoincrement=True, default=1)
    id = db.Column(db.Integer, primary_key=True)
    product_name = db.Column(db.String(100), nullable=False)
    current_price = db.Column(db.Integer, nullable=False)
    # product_picture = db.Column(db.String(1000), nullable=False)
    date_added = db.Column(db.DateTime, default=datetime.utcnow)

    
    def __str__(self):
        return '<Product %r>' % self.product_name


class Cart(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    id = db.Column(db.Integer)
    product_name = db.Column(db.String(100), nullable=False)
    current_price = db.Column(db.Integer, nullable=False)
    quantity = db.Column(db.Integer)
    total_price =db.Column(db.Integer, nullable=False, default=0)  

    # customer_link = db.Column(db.Integer, db.ForeignKey('eapp.id'), nullable=False)
    # product_link = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)

    def __str__(self):
        return '<Cart %r>' % self.id


class Order(db.Model):
    sno = db.Column(db.Integer, primary_key=True, autoincrement=True)
    id = db.Column(db.Integer)
    product_name = db.Column(db.String(1000), nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=1)
    current_price = db.Column(db.Integer, nullable=False)
    total_price =db.Column(db.Integer, nullable=False, default=0)  
    grand_total =db.Column(db.Integer, nullable=False, default=0) 

    
    # customer_link = db.Column(db.Integer, db.ForeignKey('eapp.id'), nullable=False)
    # product_link = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)


    def __str__(self):
        return '<Order %r>' % self.id

class Payment(db.Model):
    user = db.Column(db.String(1000), nullable=False)
    product_name = db.Column(db.String(1000), nullable=False)
    quantity = db.Column(db.String, nullable=False)
    price = db.Column(db.String, nullable=False)
    grand_total =db.Column(db.Integer, nullable=False, default=0)
    payment_id = db.Column(db.String(1000), nullable=False, primary_key=True)
    order_id = db.Column(db.String(1000), nullable=False)
    signature = db.Column(db.String(1000), nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow)