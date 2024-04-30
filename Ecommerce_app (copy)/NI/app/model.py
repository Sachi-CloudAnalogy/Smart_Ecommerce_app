from extensions import db
from flask_login import UserMixin

class Eapp(db.Model, UserMixin):
    __tablename__ = "eapp"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.String(5000), nullable=False, unique=True)
    password = db.Column(db.String(5000), nullable=False)
    name = db.Column(db.String(100))
    gender = db.Column(db.String(20))

    def __repr__(self):
        return f"({self.id}) {self.name},{self.gender} - {self.email} -- {self.password}"