from urllib import response
from flask import Blueprint, render_template, request, url_for, redirect
import razorpay
from .models import Order

pay_app = Blueprint("pay_app", __name__)


@pay_app.route("/pay/<int:price>/<int:sno>", methods=['GET', 'POST'])
def pay(price, sno):
    
        global payment
        client = razorpay.Client(auth=("rzp_test_ptrmZZdPzfxCgi", "jYN5J7br3pgspagq6gPRi0wt"))

        data = { "amount": price*100, "currency": "INR", "receipt": "order_rcptid_11" }
        payment = client.order.create(data=data)
        print(payment)


        dict = {'razorpay_payment_id': 'pay_O1fLoAaFGxCmDf', 'razorpay_order_id': 'order_O1f8JghI1Fzi64', 
        'razorpay_signature': '080a525cb36ed0763c0ae9fee3c56c5666064e03ff98285b3aae038e3577722e'} 
        check = client.utility.verify_payment_signature(dict)
        print(check)

        return render_template("pay.html", payment=payment, sno=sno)


    #     client.utility.verify_payment_signature({
    #    'razorpay_order_id': rp_order_id,
    #    'razorpay_payment_id': rp_payment_id,
    #    'razorpay_signature': rp_signature
    #    })

    

# {'id': 'order_O1f8JghI1Fzi64', 'entity': 'order', 'amount': 49900, 'amount_paid': 0, 'amount_due': 49900, 
# currency': 'INR', 'receipt': 'order_rcptid_11', 'offer_id': None, 'status': 'created', 'attempts': 0, 
# 'notes': [], 'created_at': 1713787675}    



