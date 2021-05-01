from app import db
from flask_login import UserMixin
from app import login_manager



class consumer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    age= db.Column(db.Integer)
    gender = db.Column(db.String(10))
    weight = db.Column(db.Float)
    height = db.Column(db.Float)
    avg_cal = db.Column(db.Float)
    userid= db.Column(db.Integer)

    def __init__(self, name, age, gender, weight, height, avg_cal, userid):
        self.name = name
        self.age = age
        self.gender = gender
        self.weight = weight
        self.height = height
        self.avg_cal = avg_cal
        self.userid = userid

class user(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id= db.Column(db.Integer)
    email = db.Column(db.String(100))    
    password = db.Column(db.String(10))
    
    def __init__(self, user_id, email, password):
        self.user_id = user_id
        self.email = email
        self.password = password

@login_manager.user_loader
def load_user(id):
    return user.query.get(int(id))