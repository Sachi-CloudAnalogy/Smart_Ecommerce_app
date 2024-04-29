# User Authentication
from flask import Flask, flash, url_for, render_template, request, redirect, session, url_for
from flask_sqlalchemy import SQLAlchemy 
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from authlib.integrations.flask_client import OAuth
import bcrypt 
import json  
import requests
from twilio.rest import Client    
import time
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv() 

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:sfdc123*@localhost:5432/flask_db'
#app.config['SECRET_KEY'] = 'secret'
db = SQLAlchemy(app)


app_conf = {"OAUTH2_CLIENT_ID": os.getenv('OAUTH2_CLIENT_ID'),
            "OAUTH2_CLIENT_SECRET": os.getenv('OAUTH2_CLIENT_SECRET'),
            "OAUTH2_META_URL": os.getenv('OAUTH2_META_URL'),
            "FLASK_SECRET": os.getenv('FLASK_SECRET'),
            "FLASK_PORT": os.getenv('FLASK_PORT')}


oauth = OAuth(app)
oauth.register("myApp",
               client_id=app_conf.get("OAUTH2_CLIENT_ID"),
               client_secret=app_conf.get("OAUTH2_CLIENT_SECRET"),
               server_metadata_url=app_conf.get("OAUTH2_META_URL"),
               client_kwargs={"scope": "openid profile email https://www.googleapis.com/auth/user.gender.read",}
                )

app.secret_key = app_conf.get("FLASK_SECRET")

# for phone number

account_sid = "ACaa062546f6a246251954bf4b6cf2bee2"
auth_token = "5ff2d511bc711411ee67db043d97980f"
verify_sid = "VA74862719853d791a2356ef7df0525f3c"
client = Client(account_sid, auth_token)


login_manager = LoginManager()     #help in logging in
login_manager.init_app(app)
login_manager.login_view = "login"

@login_manager.user_loader
def load_user(user_id):
    return Eapp.query.get(int(user_id))

class Eapp(db.Model, UserMixin):
    __tablename__ = "eapp"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.String(5000), nullable=False, unique=True)
    password = db.Column(db.String(5000), nullable=False)
    name = db.Column(db.String(100))
    gender = db.Column(db.String(20))

    def __repr__(self):
        return f"({self.id}) {self.name},{self.gender} - {self.email} -- {self.password}"

with app.app_context():
    db.create_all()

@app.route("/")
def first():
    return render_template("index.html")

@app.route("/home", methods=['GET', 'POST'])
def home():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        if email and password:
            existing_user = Eapp.query.filter_by(email=email).first()
            if existing_user:
                if bcrypt.checkpw(password.encode('utf-8'), existing_user.password.encode('utf-8')):
                    login_user(existing_user)
                    return redirect(url_for("dashboard"))
                else:
                    return "Wrong password !!"
            else:
                return "Not a registered user, need to register first!!"
        else:
            return "Both fields are required !!"      
    else: 
        return render_template("home.html")
    
@app.route("/register", methods=['GET', 'POST'])
def register():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        name = request.form.get("name")
        gender = request.form.get("gender")
        if email and password and name and gender:
            existing = Eapp.query.filter_by(email=email).first()
            if existing:
                return "Username already exist !!"
            else:
                new_pass = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')       
                new_user = Eapp(email=email, password=new_pass, name=name, gender=gender)
                db.session.add(new_user)
                db.session.commit()
                return redirect(url_for("home"))
        else:
            return "All the fields are required !!"      
    else:    
        return render_template("register.html")    


@app.route("/dashboard", methods=['GET', 'POST'])
def dashboard():
    if current_user.is_authenticated or session.get("user"):
        # User is authenticated either by Flask-Login or by Google OAuth
        return render_template("products.html", user=current_user)
    else:
        # User is not authenticated with either Flask-Login or Google OAuth
        flash("You need to be logged in to access the dashboard.", "warning")
        return redirect(url_for("home"))


@app.route("/google_login")
def google_login():
    return oauth.myApp.authorize_redirect(redirect_uri=url_for("google_callback", _external=True))

@app.route("/google_callback")
def google_callback():
    token = oauth.myApp.authorize_access_token()

    person_data_url = "https://people.googleapis.com/v1/people/me?personFields=genders"
    person_data = requests.get(person_data_url, headers={"Authorization": f"Bearer {token['access_token']}"}).json()
    token["person_data"] = person_data

    session["user"] = token       #contain id token and access token

    user = token['userinfo']
    email = user.get("email")
    gender = user.get("genders")
    name = user.get("name")
    user_exist = Eapp.query.filter_by(email=email).first()
    if user_exist:
        flash("Existing user !!", "success")
        return redirect(url_for("dashboard"))
    else:
        new_user = Eapp(email=email, password="", gender=gender, name=name)
        db.session.add(new_user)
        db.session.commit()
        flash("New User !!", "success")
        return redirect(url_for("dashboard"))



@app.route("/logout")
def logout():
    if current_user.is_authenticated:
        logout_user()  # Logout the user authenticated by Flask-Login
        return redirect(url_for("first")) 
    
    if session.get("user"):
        session.pop('user')  # Clear the Google OAuth session
        return redirect(url_for("first"))  
        


@app.route("/phone", methods=['GET', 'POST'])
def phone():
    if request.method == "POST":
        number = request.form.get('number')
        if number != "":
            session["number"] = number
            otp_verification = client.verify.services(verify_sid).verifications.create(to=number, channel="sms")
            
            return redirect(url_for("otp"))
        else:
            return "Enter Mobile Number !!"
    else:
        return render_template("enter_no.html")
    
@app.route("/otp", methods=['GET', 'POST'])
def otp():
    if request.method == "POST":
        entered_otp = request.form.get("otp")
        if entered_otp != "":
            otp_check = client.verify.services(verify_sid).verification_checks.create(to=session.get("number"), code=entered_otp)
            if otp_check.status == "approved":
                #login_user()
                return redirect(url_for("dashboard"))
            else:    
                return "Invalid OTP !!"
        else:
            return "Enter OTP !!"    
    else:  
        return render_template("enter_otp.html")    


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/show")
def show():
    user = Eapp.query.all()
    print(user)
    return "Showing all records on the terminal !!"

if __name__ == "__main__":
    app.run(debug=True)
