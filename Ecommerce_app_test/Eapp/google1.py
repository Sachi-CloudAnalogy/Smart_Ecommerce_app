import json
from flask import session, redirect, url_for, flash
from authlib.integrations.flask_client import OAuth
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from flask import Blueprint
from . import db, oauth
from .models import Eapp
import requests
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build


google_app = Blueprint("google_app", __name__)

@google_app.route("/google_login")
def google_login():
    return oauth.myApp.authorize_redirect(redirect_uri=url_for("google_app.google_callback", _external=True))

# @google_app.route("/google_callback")
# def google_callback():
#     token = oauth.myApp.authorize_access_token()
#     credentials = Credentials(token)

#     service = build('people', 'v1', credentials=credentials)
#     person = service.people().get(resourceName='people/me', personFields='genders').execute()
#     gender = person.get('genders', [])[0].get('value')
#     print("Gender:", gender)
    
#     person_data_url = "https://people.googleapis.com/v1/people/me?personFields=genders"
#     person_data = requests.get(person_data_url, headers={"Authorization": f"Bearer {token['access_token']}"}).json()
#     token["person_data"] = person_data
   
#     session["user"] = token       #contain id token and access token

#     data = json.dumps(session.get('user'))
#     print(f"DATA ----{data}")

#     user = token['userinfo']
#     email = user.get("email")
#     gender = user.get("genders")
#     name = user.get("name")

#     # Store the user's name in the session or user database
#     session["user_name"] = name


        

@google_app.route("/google_callback")
def google_callback():
    token = oauth.myApp.authorize_access_token()

    
    # Extracting user info
    credentials = Credentials(token)
    service = build('people', 'v1', credentials=credentials)
    person = service.people().get(resourceName='people/me', personFields='genders').execute()
    gender = person.get('genders', [])[0].get('value')

    # Fetching user data using API call
    person_data_url = "https://people.googleapis.com/v1/people/me?personFields=genders"
    response = requests.get(person_data_url, headers={"Authorization": f"Bearer {token['access_token']}"}).json()
    gender_from_api = response.get('genders', [])[0].get('value')

    # Storing user data in session
    session["user"] = {
        "token": token,
        "userinfo": response
    }

    user = response.get('userinfo', {})
    email = user.get("email")
    name = user.get("name")

    # Store the user's name in the session or user database
    session["user_name"] = name

    # Check if the user already exists in the database
    user_exist = Eapp.query.filter_by(email=email).first()
    if user_exist:
        return redirect(url_for("login_app.dashboard"))
    else:
        # Create a new user if not exist
        new_user = Eapp(email=email, password="", gender=gender_from_api, name=name)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for("login_app.dashboard"))

@google_app.route("/logout")
def logout():
    if current_user.is_authenticated:
        logout_user()  # Logout the user authenticated by Flask-Login

    if session.get("user"):
        session.pop('user')  # Clear the Google OAuth session

    return redirect(url_for("login_app.first"))
