# User Authentication
from flask import Flask, url_for, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy 
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
import bcrypt       #for password hashing

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:sfdc123*@localhost:5432/flask_db'
app.config['SECRET_KEY'] = 'secret'
db = SQLAlchemy(app)

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
        return render_template("home.html")
    
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
@login_required
def dashboard():
    return render_template("dashboard.html")

@app.route("/callback")
def callback():
    return "Callback"

@app.route("/logout", methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    return redirect(url_for("home"))

if __name__ == "__main__":
    app.run(debug=True)
