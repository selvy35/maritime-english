from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

db = SQLAlchemy()

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)

class Vocabulary(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    unit = db.Column(db.Integer, nullable=False)
    word = db.Column(db.String(50), nullable=False)
    meaning = db.Column(db.String(100), nullable=False)
    example = db.Column(db.String(200))
    ipa = db.Column(db.String(50))
    image = db.Column(db.String(100))

class UserProgress(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    unit = db.Column(db.Integer, nullable=False)
    section = db.Column(db.String(50), nullable=False)
    completed = db.Column(db.Boolean, default=False)
    score = db.Column(db.Integer, default=0)

class WarmUpHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    unit = db.Column(db.Integer, nullable=False)
    question = db.Column(db.String(100), nullable=False) 
    correct_answer = db.Column(db.String(10), nullable=False)  # jawaban seharusnya
    user_answer = db.Column(db.String(10), nullable=False)     # jawaban yang dipilih user
    is_correct = db.Column(db.Boolean, default=False)          # benar/salah
    timestamp = db.Column(db.DateTime, server_default=db.func.now())
