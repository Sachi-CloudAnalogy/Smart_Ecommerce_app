from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from authlib.integrations.flask_client import OAuth
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

db = SQLAlchemy()
oauth = OAuth()

app_conf = {"OAUTH2_CLIENT_ID": os.getenv('OAUTH2_CLIENT_ID'),
            "OAUTH2_CLIENT_SECRET": os.getenv('OAUTH2_CLIENT_SECRET'),
            "OAUTH2_META_URL": os.getenv('OAUTH2_META_URL'),
            "FLASK_SECRET": os.getenv('FLASK_SECRET'),
            "FLASK_PORT": os.getenv('FLASK_PORT')}

oauth.register("myApp",
               client_id=app_conf.get("OAUTH2_CLIENT_ID"),
               client_secret=app_conf.get("OAUTH2_CLIENT_SECRET"),
               server_metadata_url=app_conf.get("OAUTH2_META_URL"),
               client_kwargs={"scope": "openid profile email https://www.googleapis.com/auth/user.gender.read",}
                ) 



def create_database():
    db.create_all()
    print('Database Created')

def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://postgres:sfdc123*@localhost:5432/postgres"
    app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET')
    app.config['SERVER_NAME'] = os.getenv('SERVER_NAME', 'localhost:5000')

    db.init_app(app)

    #app.config.update(app_conf)
    oauth.init_app(app)

    login_manager = LoginManager()     #help in logging in
    login_manager.init_app(app)
    login_manager.login_view = "login"

    @login_manager.user_loader
    def load_user(user_id):
        return Eapp.query.get(int(user_id))   

    
    from .login_route import login_app
    from .google import google_app
    from .phone import phone_app
    from .models import Eapp, Cart, Product, Order, Payment
    from .product_page import product 
    from .razorpay import pay_app
    from .facebook import fb_app

    app.register_blueprint(login_app, url_prefix='/') 
    app.register_blueprint(google_app, url_prefix='/') 
    app.register_blueprint(phone_app, url_prefix='/')
    app.register_blueprint(product, url_prefix='/')
    app.register_blueprint(pay_app, url_prefix='/')
    app.register_blueprint(fb_app, url_prefix='/')


    with app.app_context():
        create_database()

    return app
