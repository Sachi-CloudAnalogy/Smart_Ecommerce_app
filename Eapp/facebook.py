from flask import Flask, render_template, redirect, session, url_for, Blueprint
from authlib.integrations.flask_client import OAuth
from flask_login import current_user, logout_user
from . import oauth
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

fb_app = Blueprint("fb_app",__name__)

@fb_app.route('/facebook_login')
def facebook_login():
   
    FACEBOOK_CLIENT_ID = os.getenv('FACEBOOK_CLIENT_ID')      
    FACEBOOK_CLIENT_SECRET = os.getenv('FACEBOOK_CLIENT_SECRET')    
    oauth.register(
        name='facebook',
        client_id=FACEBOOK_CLIENT_ID,
        client_secret=FACEBOOK_CLIENT_SECRET,
        access_token_url='https://graph.facebook.com/oauth/access_token',
        access_token_params=None,
        authorize_url='https://www.facebook.com/dialog/oauth',
        authorize_params=None,
        api_base_url='https://graph.facebook.com/',
        client_kwargs={'scope': 'email'},
    )
    redirect_uri = url_for('fb_app.facebook_auth', _external=True)
    return oauth.facebook.authorize_redirect(redirect_uri)

@fb_app.route('/facebook/auth/')
def facebook_auth():
    token = oauth.facebook.authorize_access_token()
    resp = oauth.facebook.get('https://graph.facebook.com/me?fields=id,name,email,picture{url}')
    profile = resp.json()
    print("Facebook User ", profile)
    
    # session['facebook_token'] = (resp['access_token'], '')
    # user_info = resp.get
    # user_email = user_info.data['email']
    
    return redirect(url_for("login_app.dashboard"))

@fb_app.route("/logout")
def logout():
    if current_user.is_authenticated:
        logout_user()  # Logout the user authenticated by Flask-Login
    
    if session.get("user"):
        session.pop('user')  # Clear the Google OAuth session

    if "facebook_token" in session:
        session.pop("facebook_token")  # Clear the Facebook token from the session

    return redirect(url_for("login_app.first"))