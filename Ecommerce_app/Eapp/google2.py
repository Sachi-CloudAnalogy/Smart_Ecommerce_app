import json
from flask import session, redirect, url_for, flash
from authlib.integrations.flask_client import OAuth
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from flask import Blueprint
from . import db, oauth
from .models import Eapp
import requests


# app_conf = {"OAUTH2_CLIENT_ID": "135553744176-spo97g44ksc0d2nqp88pakpg9f1seauf.apps.googleusercontent.com",
#             "OAUTH2_CLIENT_SECRET": "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",
#             "OAUTH2_META_URL": "https://accounts.google.com/.well-known/openid-configuration",
#             "FLASK_SECRET": "secret",
#             "FLASK_PORT": 5000}

# oauth = OAuth()
# oauth.register("myApp",
#                client_id=app_conf.get("OAUTH2_CLIENT_ID"),
#                client_secret=app_conf.get("OAUTH2_CLIENT_SECRET"),
#                server_metadata_url=app_conf.get("OAUTH2_META_URL"),
#                client_kwargs={"scope": "openid profile email https://www.googleapis.com/auth/user.gender.read",}
#                 )

google_app = Blueprint("google_app", __name__)

@google_app.route("/google_login")
def google_login():
    return oauth.myApp.authorize_redirect(redirect_uri=url_for("google_app.google_callback", _external=True))

@google_app.route("/google_callback")
def google_callback():
    token = oauth.myApp.authorize_access_token()

    person_data_url = "https://people.googleapis.com/v1/people/me?personFields=genders"
    person_data = requests.get(person_data_url, headers={"Authorization": f"Bearer {token['access_token']}"}).json()
    token["person_data"] = person_data


    print(token)
    print(f" Gender ---- {token['person_data']['genders']}")
    # data = json.dumps(session.get('user'))
    # print(f"Data - {data}")


    session["user"] = token       #contain id token and access token
    user = token['userinfo']
    print(f"*****{user}****")

    email = user.get("email")
    gender = user.get("genders")
    name = user.get("name")
    user_exist = Eapp.query.filter_by(email=email).first()
    if user_exist:
        # flash("Existing user !!", "success")
        return redirect(url_for("login_app.dashboard"))
    else:
        new_user = Eapp(email=email, password="", gender=gender, name=name)
        db.session.add(new_user)
        db.session.commit()
        # flash("New User !!", "success")
        return redirect(url_for("login_app.dashboard"))



@google_app.route("/logout")
def logout():
    if current_user.is_authenticated:
        logout_user()  # Logout the user authenticated by Flask-Login
        return redirect(url_for("login_app.first")) 
    
    if session.get("user"):
        session.pop('user')  # Clear the Google OAuth session
        return redirect(url_for("login_app.first"))  
        

