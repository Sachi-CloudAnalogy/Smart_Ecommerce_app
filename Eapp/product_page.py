from urllib import response
from flask import Blueprint, render_template, request, flash, redirect, session, url_for
from flask_login import current_user
from .models import Product, Cart, Order, Payment
from . import db
from .google import google_app

product = Blueprint("product", __name__)

@product.route("/products", methods=['GET', 'POST'])
def products():
    if request.method == 'POST':
        product_name = request.form.get("product_name")
        current_price = request.form.get("current_price")
        previous_price = request.form.get("previous_price")
        in_stock = request.form.get("in_stock")
        # product_picture = request.form.get("product_picture")
        if product_name == "" or current_price == "" or previous_price == "" or in_stock == "":
            return "Fill all the fields"
        else:
            new_item = Product(product_name=product_name, current_price=current_price, previous_price=previous_price,
                            in_stock=in_stock)
            db.session.add(new_item)
            db.session.commit()
            flash(f"{product_name} is added successfully !!")
            return redirect(url_for("product.show_added_item"))

    return render_template("add_item.html")

@product.route("/show_added_item", methods=['GET','POST'])
def show_added_item():
    items = Product.query.order_by(Product.date_added).all()
    return render_template("product.html", items=items)

@product.route("/cart/<int:id>", methods=['GET', 'POST'])
def cart(id):
    item = Product.query.filter_by(id=id).first()
    if item and request.method == "POST":
        quantity = request.form.get("quantity")
        new_item = Cart(id=item.id, product_name=item.product_name, previous_price=item.previous_price, 
                        current_price=item.current_price, quantity=quantity)
        db.session.add(new_item)
        db.session.commit()

        items = Cart.query.filter_by(sno=new_item.sno).first()
        return render_template("cart.html", item=items)
    else:
        items = Product.query.filter_by(id=item.id).first()
        return render_template("cart.html", item=items)
    
@product.route("/cart/delete/<int:id>", methods=['GET', 'POST'])   
def cart_del(id):
    item = Product.query.filter_by(id=id).first()
    db.session.delete(item)
    db.session.commit()
    return redirect(url_for("login_app.dashboard"))
    

    
@product.route("/payment/<int:id>/<int:sno>", methods=['GET','POST'])
def payment(id, sno):
    item = Cart.query.filter_by(sno=sno).first()
    if item:
        new_item = Order(id=item.id, product_name=item.product_name, current_price=item.current_price, quantity=item.quantity, 
                         total_price=item.current_price*item.quantity)
        db.session.add(new_item)
        db.session.commit()
        return render_template("payment.html", item=new_item)
    else:
        return "Something went wrong !!"
    

@product.route("/end/<int:sno>", methods=['GET', 'POST'])
def end(sno):
    item = Order.query.filter_by(sno=sno).first()
    product_name = item.product_name
    quantity = item.quantity
    payment_id = request.args.get("payment_id")
    order_id = request.args.get("order_id")
    signature = request.args.get("signature")
    if current_user:
        user = current_user.name
    elif session["user"]:     
        user = google_app.token['userinfo']
        name = user.get("name")     
    new_entry = Payment(user=user, product_name=product_name, quantity=quantity, payment_id=payment_id, order_id=order_id, signature=signature)
    db.session.add(new_entry)
    db.session.commit()

    return render_template("end.html", payment_id=payment_id, order_id=order_id, signature=signature)    