from flask import Blueprint, request, url_for, render_template, session, redirect
from twilio.rest import Client
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()  

phone_app = Blueprint("phone_app", __name__)

account_sid = os.getenv('Account_sid')
auth_token = os.getenv('Auth_token')
verify_sid = os.getenv('Verify_sid')
client = Client(account_sid, auth_token)


@phone_app.route("/phone", methods=['GET', 'POST'])
def phone():
    if request.method == "POST":
        number = request.form.get('number')
        if number != "":
            session["number"] = number
            otp_verification = client.verify.services(verify_sid).verifications.create(to=number, channel="sms")
            
            return redirect(url_for("phone_app.otp"))
        else:
            return "Enter Mobile Number !!"
    else:
        return render_template("enter_no.html")
    
@phone_app.route("/otp", methods=['GET', 'POST'])
def otp():
    if request.method == "POST":
        entered_otp = request.form.get("otp")
        if entered_otp != "":
            otp_check = client.verify.services(verify_sid).verification_checks.create(to=session.get("number"), code=entered_otp)
            if otp_check.status == "approved":
                #login_user()
                return redirect(url_for("login_app.dashboard"))
            else:    
                return "Invalid OTP !!"
        else:
            return "Enter OTP !!"    
    else:  
        return render_template("enter_otp.html")