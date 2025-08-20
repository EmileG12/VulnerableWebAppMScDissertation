from sqlalchemy import event
import hashlib
from flask_login import UserMixin

from . import db

class User(UserMixin, db.Model):
    userid = db.Column(db.Integer, primary_key=True) # primary keys are required by SQLAlchemy
    name = db.Column(db.String(1000))
    username = db.Column(db.String(1000))
    userhash = db.Column(db.String(1000))
    password = db.Column(db.String(100))
    admin = db.Column(db.Boolean, default=False,nullable=False)
    
    def get_id(self):
        return str(self.userid)

class Credit(db.Model):
    userid = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(1000))
    number = db.Column(db.Integer)
    CVV = db.Column(db.Integer)

@event.listens_for(User.__table__, 'after_create')
def create_users(*args, **kwargs):
    a = hashlib.md5("Jacksparrow".encode(encoding='UTF-8'))
    b = hashlib.md5("Barbossa".encode(encoding='UTF-8'))
    c = hashlib.md5("Johnnydepp".encode(encoding= 'UTF-8'))
    jackhex = a.hexdigest()
    barbhex = b.hexdigest()
    johnhex = c.hexdigest()

    db.session.add(User(userid=1, name="Jack Sparrow", username="Jacksparrow",userhash=jackhex, password="princess", admin=True))
    db.session.add(User(userid=2, name="Barbossa", username="Barbossa", userhash=barbhex, password="Blackpearl", admin=False))
    db.session.add(User(userid=3, name="Johnny Depp", username="Johnnydepp", userhash=johnhex, password="Pirates", admin=False))
    db.session.commit()

@event.listens_for(Credit.__table__, 'after_create')
def create_credit(*args,**kwargs):
    db.session.add(Credit(userid=1, name="Jack Sparrow", number="371449635398431", CVV=108))
    db.session.add(Credit(userid=2, name="Barbossa", number="5063516945005047", CVV=983))
    db.session.add(Credit(userid=3, name="Johnny Depp", number="6011514433500000", CVV=123))
    db.session.commit()
    