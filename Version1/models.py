from flask_sqlalchemy import SQLAlchemy

db=SQLAlchemy()

class Admin(db.Model):
    __tablename__= 'librarian'
    full_name=db.Column(db.String(50), nullable=False)
    username=db.Column(db.String(50), unique=True, nullable=False, primary_key=True)
    password = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(100), nullable =False)
    mob_num = db.Column(db.Integer, nullable=False)
    profile_photo_path = db.Column(db.String(255),nullable=False)

class User(db.Model):
    __tablename__='users'
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(50), nullable= False)
    username=db.Column(db.String(50), unique=True, nullable = False)
    password = db.Column(db.String(100),  nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    mob_num = db.Column(db.Integer, nullable = False)
    profile_photo_path = db.Column(db.String(255), nullable=False)
    books= db.relationship('Book', backref='user')
    ebook_return = db.relationship('EbookReturn', backref='user')
    feedbacks = db.relationship('FeedBack', backref='user')

class Book(db.Model):
    __tablename__='books'
    id=db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), unique=True, nullable=False)
    author = db.Column(db.String(50), nullable=False)
    preview_path = db.Column(db.String(255), nullable = False)
    Content = db.Column(db.String(255), nullable = False)
    genre = db.Column(db.String, db.ForeignKey('genres.genre'))
    renter_id=db.Column(db.Integer, db.ForeignKey('users.id'))
    is_available = db.Column(db.Boolean, default = True)
    ebook_return = db.relationship('EbookReturn', backref = 'book')
    feedbacks = db.relationship('FeedBack', backref = 'book')

class Genre(db.Model):
    __tablename__='genres'
    genre = db.Column(db.String(100), unique=True, nullable=False, primary_key=True)
    description = db.Column(db.String(50), nullable=False)

class RentalRequest(db.Model):
    __tablename__ = 'rental_requests'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey('books.id'), nullable=False)
    status = db.Column(db.Enum('Pending', 'Approved', 'Rejected'), default='Pending', nullable=False)
    issued_date = db.Column(db.DateTime, nullable=True)
    user = db.relationship('User', backref='rental_requests')
    book = db.relationship('Book', backref='rental_requests')


class EbookReturn(db.Model):
    __tablename__ = 'ebook_returns'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey('books.id'), nullable=False)
    return_date = db.Column(db.DateTime)

class FeedBack(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    book_id = db.Column(db.Integer, db.ForeignKey('books.id'), default='Removed Book', nullable = False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), default='Removed User' ,nullable = False)
    feedback = db.Column(db.Text, nullable = True)
    rating = db.Column(db.Integer, nullable = True)
