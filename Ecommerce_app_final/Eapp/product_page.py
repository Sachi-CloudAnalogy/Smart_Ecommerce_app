from urllib import response
from flask import Blueprint, render_template, request, flash, redirect, session, url_for
from flask_login import current_user
from .models import Product, Cart, Order, Payment
from . import db

product = Blueprint("product", __name__)

@product.route("/products", methods=['GET', 'POST'])
def products():
    if request.method == 'POST':
        product_name = request.form.get("product_name")
        current_price = request.form.get("current_price")
        # product_picture = request.form.get("product_picture")
        if product_name == "" or current_price == "" :
            return "Fill all the fields"
        else:
            new_item = Product(product_name=product_name, current_price=current_price)
            db.session.add(new_item)
            db.session.commit()
            flash(f"{product_name} is added successfully !!")
            return redirect(url_for("product.show_added_item"))

    return render_template("add_item.html")

@product.route("/show_added_item", methods=['GET','POST'])
def show_added_item():
    items = Product.query.order_by(Product.date_added).all()
    return render_template("product.html", items=items)

@product.route("/carts")
def carts():
    items = Cart.query.all()
    if items:
        grand_total = 0
        for item in items:
            grand_total += item.total_price
            return render_template("cart2.html", items=items, grand_total=grand_total)
    else:
        return "<h1>Cart is Empty !!</h1>"    


@product.route("/cart/<int:id>", methods=['GET', 'POST'])
def cart(id):
    item = Product.query.filter_by(id=id).first()
    if item:
        if request.method == "POST":
            quantity = request.form.get("quantity")
            total_price=int(item.current_price)*int(quantity)
            new_item = Cart(id=item.id, product_name=item.product_name,
                            current_price=item.current_price, quantity=quantity, total_price=total_price)
            db.session.add(new_item)
            db.session.commit()

            items = Cart.query.all()
            grand_total = 0
            for item in items:
                grand_total += item.total_price
            return render_template("cart2.html", items=items, grand_total=grand_total)
        else:
            items = []
            items.append(item)
            return render_template("cart2.html", items=items, grand_total=item.current_price)
    else:
        items = Cart.query.all()
        grand_total = 0
        for item in items:
            grand_total += item.total_price
        return render_template("cart2.html", items=items, grand_total=grand_total)
        
    
@product.route("/cart/delete/<int:sno>", methods=['GET', 'POST'])   
def cart_del(sno):
    item = Cart.query.filter_by(sno=sno).first()
    if item:
        db.session.delete(item)
        db.session.commit()

    item = Order.query.filter_by(sno=sno).first()
    if item:
        db.session.delete(item)
        db.session.commit()
    return redirect(url_for("product.carts"))
    
# @product.route("/cart/delete/<int:sno>", methods=['GET', 'POST'])   
# def cart_del(sno):
#     # Capture the current URL before deleting the item
#     referer_url = request.headers.get('Referer')
    
#     item = Cart.query.filter_by(sno=sno).first()
#     db.session.delete(item)
#     db.session.commit()

#     item = Order.query.filter_by(sno=sno).first()
#     db.session.delete(item)
#     db.session.commit()
    
#     # Redirect back to the captured URL
#     return redirect(referer_url)
    
@product.route("/payment/<int:total>", methods=['GET','POST'])
def payment(total):
    items = Cart.query.all()
    for item in items:
        new_item = Order(id=item.id, product_name=item.product_name, current_price=item.current_price, quantity=item.quantity, 
                         total_price=item.current_price*item.quantity, grand_total=total)
        db.session.add(new_item)
        db.session.commit()
    return render_template("payment.html", items=items, total=total)
   
    

@product.route("/end/<int:price>", methods=['GET', 'POST'])
def end(price):
    items = Cart.query.all()
    product_names = []
    quantities = []
    prices = []
    for item in items:
        product_names.append(item.product_name)
        quantities.append(item.quantity)
        prices.append(item.current_price)

    # Convert lists to strings
    product_names_str = ', '.join(product_names)
    quantities_str = ', '.join(str(qty) for qty in quantities) 
    price_str = ', '.join(str(price_tag) for price_tag in prices)   
    if current_user.is_authenticated:
        user = current_user.name
    else:
        user = session.get("user_name")
    grand_total = price
    payment_id = request.args.get("payment_id")
    order_id = request.args.get("order_id")
    signature = request.args.get("signature")
    new_entry = Payment(user=user, product_name=product_names_str, quantity=quantities_str, price=price_str, grand_total=grand_total, 
                        payment_id=payment_id, order_id=order_id, signature=signature)
    db.session.add(new_entry)
    db.session.commit()

    # Deleting all data from the Cart table
    Cart.query.delete()
    db.session.commit()

    return render_template("end.html", payment_id=payment_id, order_id=order_id, signature=signature)    