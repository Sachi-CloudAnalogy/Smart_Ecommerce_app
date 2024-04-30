# User Authentication
from flask import Flask, flash, url_for, render_template, request, redirect, session, url_for
from flask_sqlalchemy import SQLAlchemy 
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from authlib.integrations.flask_client import OAuth
import bcrypt 
import json   
import os   


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:sfdc123*@localhost:5432/flask_db'
app.config['SECRET_KEY'] = 'secret'
db = SQLAlchemy(app)
app_conf = {"OAUTH2_CLIENT_ID": "135553744176-spo97g44ksc0d2nqp88pakpg9f1seauf.apps.googleusercontent.com",
            "OAUTH2_CLIENT_SECRET": "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",
            "OAUTH2_META_URL": "https://accounts.google.com/.well-known/openid-configuration",
            "FLASK_SECRET": "secret",
            "FLASK_PORT": 5000}

oauth = OAuth(app)
oauth.register("myApp",
               client_id=app_conf.get("OAUTH2_CLIENT_ID"),
               client_secret=app_conf.get("OAUTH2_CLIENT_SECRET"),
               server_metadata_url=app_conf.get("OAUTH2_META_URL"),
               client_kwargs={"scope": "openid profile email",}
                )

app.secret_key = app_conf.get("FLASK_SECRET")


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

    def __repr__(self):
        return f"({self.id}) {self.email} -- {self.password}"

with app.app_context():
    db.create_all()

@app.route("/", methods=['GET', 'POST'])
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
        return render_template("home.html", session = session.get("user"),
                           data=json.dumps(session.get("user"), indent=4))
    
@app.route("/register", methods=['GET', 'POST'])
def register():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        if email and password:
            existing = Eapp.query.filter_by(email=email).first()
            if existing:
                return "Username already exist !!"
            else:
                new_pass = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')       
                new_user = Eapp(email=email, password=new_pass)
                db.session.add(new_user)
                db.session.commit()
                return redirect(url_for("home"))
        else:
            return "Both fields are required !!"      
    else:    
        return render_template("register.html")    

@app.route("/dashboard", methods=['GET', 'POST'])
# @login_required
def dashboard():
    return render_template("dashboard.html")


# @app.route("/logout", methods=['GET', 'POST'])
# @login_required
# def logout():
#     logout_user()
#     return redirect(url_for("home"))

@app.route("/google_login")
def google_login():
    return oauth.myApp.authorize_redirect(redirect_uri=url_for("google_callback", _external=True))

@app.route("/google_callback")
def google_callback():
    token = oauth.myApp.authorize_access_token()
    session["user"] = token       #contain id token and access token

    user = token['userinfo']
    email = user.get("email")
    user_exist = Eapp.query.filter_by(email=email).first()
    if user_exist:
        flash("Existing user !!")
        return redirect(url_for("dashboard"))
    else:
        new_user = Eapp(email=email, password="")
        db.session.add(new_user)
        db.session.commit()
        flash("New User !!")
        return redirect(url_for("dashboard"))

@app.route("/logout")
def logout():
    session.pop('user', None)
    return redirect(url_for("home"))

@app.route('/facebook_login')
def facebook_login():
   
    FACEBOOK_CLIENT_ID = "594263754976083"      
    FACEBOOK_CLIENT_SECRET = "021b367ffb4c207f90b9c9addf8db09b"    
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
    redirect_uri = url_for('facebook_auth', _external=True)
    return oauth.facebook.authorize_redirect(redirect_uri)

@app.route('/facebook/auth/')
def facebook_auth():
    token = oauth.facebook.authorize_access_token()
    resp = oauth.facebook.get('https://graph.facebook.com/me?fields=id,name,email,picture{url}')
    profile = resp.json()
    print("Facebook User ", profile)
    return redirect(url_for("dashboard"))

@app.route("/show")
def show():
    user = Eapp.query.all()
    print(user)
    return "Showing all records on the terminal !!"

if __name__ == "__main__":
    app.run(debug=True)
