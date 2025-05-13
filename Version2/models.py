from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    full_name = db.Column(db.String(120), nullable = False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(50), nullable=False)
    is_active = db.Column(db.Boolean, default=True) 

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.username}'
    
class Genre(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique = True, nullable=False)
    description = db.Column(db.Text, nullable=True)
    image = db.Column(db.String(200), nullable=True) 
    date_created = db.Column(db.Date, nullable = True, default= datetime.utcnow().date())


class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False)
    author = db.Column(db.String(120), nullable=False)
    image = db.Column(db.String(100), nullable=True)
    content = db.Column(db.String, nullable=True)
    rating = db.Column(db.Float, nullable=True)
    genre_id = db.Column(db.Integer, db.ForeignKey('genre.id'), nullable=False)
    genre = db.relationship('Genre', backref=db.backref('books', lazy=True))
    is_available = db.Column(db.Boolean, default=True)

class RentalRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey('book.id'), nullable=False)
    status = db.Column(db.String(20), default='pending')
    date_requested = db.Column(db.DateTime, default=datetime.utcnow)
    date_issued = db.Column(db.DateTime, default=datetime.utcnow)
    user = db.relationship('User', backref=db.backref('rental_requests', lazy=True))
    book = db.relationship('Book', backref=db.backref('rental_requests', lazy=True))

    def __repr__(self):
        return f'<RentalRequest {self.id} by User {self.user_id} for Book {self.book_id}>'