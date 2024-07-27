from . import db
from datetime import datetime

class Student(db.Model):
    __tablename__ = 'students'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False)
    class_name = db.Column(db.String(64), nullable=False)
    address = db.Column(db.String(128), nullable=False)
    fingerprint = db.Column(db.String(64), nullable=False)
    

    loans = db.relationship('Loan', backref='student', lazy=True, cascade='all, delete-orphan')

class Book(db.Model):
    __tablename__ = 'books'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(256), nullable=True)
    ISBN = db.Column(db.String(256), nullable=False)
    author = db.Column(db.String(256), nullable=True)
    year = db.Column(db.String(256), nullable=True)
    publisher = db.Column(db.String(256), nullable=True)
    image_url = db.Column(db.String(256), nullable=True)
    loans = db.relationship('Loan', backref='book', lazy=True, cascade='all, delete-orphan')

class Loan(db.Model):
    __tablename__ = 'loans'
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey('books.id'), nullable=False)
    loan_date = db.Column(db.Date, nullable=False, default=datetime.utcnow)
    return_date = db.Column(db.Date, nullable=False)
    is_return = db.Column(db.Boolean, nullable=True, default=False)