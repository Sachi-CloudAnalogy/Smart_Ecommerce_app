from flask import Flask
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from flask_sqlalchemy import SQLAlchemy
from extensions import db
from model import Eapp
from route.google import google
from route.main_route import main
from route.phone import app
from authlib.integrations.flask_client import OAuth

app = Flask(__name__)
app.register_blueprint(google)
app.register_blueprint(main)
app.register_blueprint(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:sfdc123*@localhost:5432/flask_db'
db = SQLAlchemy(app)
app.config['SECRET_KEY'] = 'secret'

db.init_app(app)
with app.app_context():
    db.create_all()

login_manager = LoginManager()     #help in logging in
login_manager.init_app(app)
login_manager.login_view = "login"

@login_manager.user_loader
def load_user(user_id):
    return Eapp.query.get(int(user_id))  

oauth = OAuth(app)



if __name__ == "__main__":
    app.run(debug=True)