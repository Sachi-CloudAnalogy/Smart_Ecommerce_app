import bcrypt
from flask import Blueprint, flash, redirect, render_template, request, session, url_for
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from . import db
from .models import Eapp
# from flask_dance.contrib.facebook import facebook


login_app = Blueprint('login_app', __name__)

@login_app.route("/")
def first():
    return render_template("index.html")

@login_app.route("/home", methods=['GET', 'POST'])
def home():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        if email and password:
            existing_user = Eapp.query.filter_by(email=email).first()
            if existing_user:
                if bcrypt.checkpw(password.encode('utf-8'), existing_user.password.encode('utf-8')):
                    login_user(existing_user)
                    return redirect(url_for("login_app.dashboard"))
                else:
                    return "Wrong password !!"
            else:
                return "Not a registered user, need to register first!!"
        else:
            return "Both fields are required !!"      
    else: 
        return render_template("home.html")
    
@login_app.route("/register", methods=['GET', 'POST'])
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
                return redirect(url_for("login_app.home"))
        else:
            return "All the fields are required !!"      
    else:    
        return render_template("register.html")    


# @login_app.route("/dashboard", methods=['GET', 'POST'])
# def dashboard():
#     if current_user.is_authenticated or session.get("user"):
#         # User is authenticated either by Flask-Login or by Google OAuth
#         return render_template("dashboard.html", user=current_user)
#     else:
#         # User is not authenticated with either Flask-Login or Google OAuth
#         flash("You need to be logged in to access the dashboard.", "warning")
#         return redirect(url_for("login_app.home"))
    
@login_app.route("/dashboard", methods=['GET', 'POST'])
def dashboard():
    if current_user.is_authenticated or session.get("user"):
        # User is authenticated either by Flask-Login or by Facebook OAuth
        return render_template("dashboard.html", user=current_user)
    elif "facebook_token" in session:
        # User is authenticated with Facebook OAuth
        # You can retrieve user information from the session or call Facebook API if needed
        return render_template("dashboard.html", user=session["user"])
    else:
        # User is not authenticated with Flask-Login or Facebook OAuth
        flash("You need to be logged in to access the dashboard.", "warning")
        # Redirect the user to the Facebook login route
        return redirect(url_for("fb_app.facebook_login"))


# @login_app.route("/logout")
# def logout():
#     if current_user.is_authenticated:
#         logout_user()  # Logout the user authenticated by Flask-Login
#         return redirect(url_for("login_app.first")) 
    
#     if session.get("user"):
#         session.pop('user')  # Clear the Google OAuth session
#         return redirect(url_for("login_app.first"))  

@login_app.route("/logout")
def logout():
    if current_user.is_authenticated:
        logout_user()  # Logout the user authenticated by Flask-Login
    
    if session.get("user"):
        session.pop('user')  # Clear the Google OAuth session

    if "facebook_token" in session:
        session.pop("facebook_token")  # Clear the Facebook token from the session

    return redirect(url_for("login_app.first"))     
    
@login_app.route("/about")
def about():
    return render_template("about.html")


@login_app.route("/show")
def show():
    user = Eapp.query.all()
    print(user)
    return "Showing all records on the terminal !!"
