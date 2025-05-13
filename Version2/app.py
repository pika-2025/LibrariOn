from flask import Flask, render_template, request, jsonify, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from models import db, User, Genre, Book, RentalRequest
import os
from werkzeug.utils import secure_filename
from datetime import datetime, timedelta
from celery import Celery
from flask_caching import Cache
from celery.schedules import crontab


app = Flask(__name__, static_folder='static', template_folder='templates')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['JWT_SECRET_KEY'] = '22f3002119'
app.config['CELERY_BROKER_URL'] = 'redis://localhost:6380/0'
app.config['CELERY_RESULT_BACKEND'] = 'redis://localhost:6380/0'
app.config['CACHE_TYPE'] = 'RedisCache'
app.config['CACHE_REDIS_HOST'] = 'localhost'
app.config['CACHE_REDIS_PORT'] = 6380
app.config['CACHE_REDIS_DB'] = 0
app.config['CACHE_REDIS_URL'] = 'redis://localhost:6380/0'
app.config['CACHE_DEFAULT_TIMEOUT'] = 300



db.init_app(app)
migrate = Migrate(app, db)
jwt = JWTManager(app)
cache=Cache(app)
cache.init_app(app)

def make_celery(app: Flask) -> Celery:
    celery = Celery(
        app.import_name,
        backend=app.config['CELERY_RESULT_BACKEND'],
        broker=app.config['CELERY_BROKER_URL']
    )
    celery.conf.update(app.config)
    class ContextTask(celery.Task):
        def _call_(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)
    celery.Task = ContextTask
    celery.conf.beat_schedule = {
        'send-monthly-activity-report': {
            'task': 'send_monthly_activity_report',
            'schedule': crontab(day_of_month=1, hour=0, minute=0),  # Run at midnight on the 1st of every month
        },
    }
    return celery

celery = make_celery(app)


@app.route('/')
def index():
    return render_template('index.html')



@app.route('/register', methods=['POST'])
def register():
    data = request.json
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    full_name = data.get('full_name')
    role = 'user'
    if not User.query.filter_by(role='librarian').first():
        role = 'librarian'
    if User.query.filter_by(username=username).first():
        return jsonify({'error': 'Username already exists'}), 400
    if User.query.filter_by(email=email).first():
        return jsonify({'error': 'Email already exists'}), 400        
    new_user = User(username=username, email=email, role=role, full_name = full_name)
    new_user.set_password(password)
    db.session.add(new_user)
    db.session.commit()
    return jsonify({'message': 'User registered successfully'}), 201



@app.route('/check_librarian', methods=['GET'])
def check_librarian():
    librarian_exists = User.query.filter_by(role='librarian').first() is not None
    return jsonify({'librarian_exists': librarian_exists}), 200


@app.route('/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    user = User.query.filter_by(username=username).first()
    if user and user.check_password(password) and user.is_active: #will add is_active
        access_token = create_access_token(identity={'username': user.username, 'role': user.role})
        return jsonify({'access_token': access_token}), 200
    else:
        return jsonify({'error': 'Invalid username or password'}), 401



@app.route('/user_info', methods=['GET'])
@jwt_required()
def user_info():
    current_user = get_jwt_identity()
    user = User.query.filter_by(username=current_user['username']).first()
    if user:
        return jsonify({
            'username': user.username,
            'role': user.role,
            'full_name': user.full_name,
            'email': user.email
        }), 200
    else:
        return jsonify({'error': 'User not found'}), 404



@app.route('/liboard/genres', methods=['POST'])
@jwt_required()
def add_genre():
    current_user = get_jwt_identity()
    if current_user['role'] != 'librarian':
        return jsonify({'error': 'Unauthorized'}), 403
    name = request.form.get('name')
    description = request.form.get('description')
    image = request.files.get('image')
    if image:
        image_filename = secure_filename(image.filename)
        image_path = os.path.join(app.config['UPLOAD_FOLDER'], image_filename)
        image.save(image_path)
    else:
        image_path = None 

    new_genre = Genre(name=name, description=description, image=image_path)
    db.session.add(new_genre)
    db.session.commit()    
    return jsonify({'message': 'Genre added successfully'}), 201



@app.route('/liboard/genres', methods=['GET'])
@jwt_required()
@cache.cached(timeout=300, key_prefix="general")
def get_genres():
    current_user = get_jwt_identity()
    if current_user['role'] != 'librarian':
        return jsonify({'error': 'Unauthorized'}), 403
    genres = Genre.query.all()
    genres_list = [{
        'id': genre.id,
        'name': genre.name,
        'description': genre.description,
        'image': genre.image,
        'date_created': genre.date_created.strftime('%d-%m-%y')
    } for genre in genres]
    print(genres_list)  # Debugging line
    return jsonify(genres_list), 200



@app.route('/liboard/genres/<int:genre_id>/books', methods=['GET'])
@jwt_required()
def get_genre_books(genre_id):
    current_user = get_jwt_identity()
    if current_user['role'] != 'librarian':
        return jsonify({'error': 'Unauthorized'}), 403
    genre = Genre.query.get_or_404(genre_id)
    books = Book.query.filter_by(genre_id=genre.id).all()
    books_list = [{
        'id': book.id,
        'title': book.title,
        'author': book.author,
        'image': book.image,
        'content': book.content,
    } for book in books]   
    return jsonify({'genre': {'id': genre.id, 'name': genre.name}, 'books': books_list}), 200



@app.route('/liboard', methods=['GET'])
@jwt_required()
def get_rental_requests():
    current_user = get_jwt_identity()
    if current_user['role'] != 'librarian':
        return jsonify({'error': 'Unauthorized'}), 403
    rental_requests = RentalRequest.query.all()
    requests_list = [{
        'id': req.id,
        'user': req.user.username,
        'book': req.book.title,
        'image': req.book.image,
        'status': req.status,
        'date_requested': req.date_requested.strftime('%d-%m-%Y')
    } for req in rental_requests]
    return jsonify({'rental_requests': requests_list}), 200



@app.route('/liboard/rental_requests/<int:request_id>/accept', methods=['POST'])
@jwt_required()
def accept_rental_request(request_id):
    current_user = get_jwt_identity()
    if current_user['role'] != 'librarian':
        return jsonify({'error': 'Unauthorized'}), 403
    rental_request = RentalRequest.query.get_or_404(request_id)
    if rental_request.status != 'pending':
        return jsonify({'error': 'Request already processed'}), 400
    rental_request.status = 'accepted'
    db.session.commit()

    return jsonify({'message': 'Request accepted'}), 200



@app.route('/liboard/rental_requests/<int:request_id>/reject', methods=['POST'])
@jwt_required()
def reject_rental_request(request_id):
    current_user = get_jwt_identity()
    if current_user['role'] != 'librarian':
        return jsonify({'error': 'Unauthorized'}), 403
    rental_request = RentalRequest.query.get_or_404(request_id)
    if rental_request.status != 'pending':
        return jsonify({'error': 'Request already processed'}), 400
    rental_request.status = 'rejected'
    rental_request.book.is_available = True
    db.session.commit()
    return jsonify({'message': 'Request rejected'}), 200



@app.route('/liboard/genres/<int:genre_id>/books', methods=['POST'])
@jwt_required()
def add_genre_book(genre_id):
    current_user = get_jwt_identity()
    if current_user['role'] != 'librarian':
        return jsonify({'error': 'Unauthorized'}), 403
    title = request.form.get('title')
    author = request.form.get('author')
    price = request.form.get('price')
    image = request.files.get('image')
    content = request.files.get('content')
    if image:
        image_filename = secure_filename(image.filename)
        image_path = os.path.join(app.config['UPLOAD_FOLDER'], image_filename)
        image.save(image_path)
    else:
        image_filename = None
    if content:
        content_filename = secure_filename(content.filename)
        content_path = os.path.join(app.config['UPLOAD_FOLDER'], content_filename)
        content.save(content_path)
    else:
        content_filename = None
    new_book = Book(
        title=title, 
        author=author, 
        genre_id=genre_id, 
        image=image_path, 
        content=content_path
    )
    db.session.add(new_book)
    db.session.commit()
    return jsonify({'message': 'Book added successfully'}), 201


@app.route('/liboard/books/<int:book_id>', methods=['DELETE'])
@jwt_required()
def delete_book(book_id):
    book = Book.query.get(book_id)
    if book is None:
        return jsonify({'error': 'Book not found'}), 404   
    db.session.delete(book)
    db.session.commit()
    return jsonify({'message': 'Book deleted successfully'}), 200



@app.route('/liboard/genres/<int:genre_id>', methods=['DELETE'])
@jwt_required()
def delete_genre(genre_id):
    current_user = get_jwt_identity()
    if current_user['role'] != 'librarian':
        return jsonify({'error': 'Unauthorized'}), 403

    genre = Genre.query.get(genre_id)
    if not genre:
        return jsonify({'error': 'Genre not found'}), 404

    try:
        db.session.delete(genre)
        db.session.commit()
        return jsonify({'message': 'Genre deleted successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500



@app.route('/liboard/users', methods=['GET'])
@jwt_required()
def get_all_users():
    current_user = get_jwt_identity()
    if current_user['role'] != 'librarian':
        return jsonify({'error': 'Unauthorized'}), 403
    users = User.query.all()
    users_list = [{
        'id': user.id,
        'full_name': user.full_name,
        'username': user.username,
        'email': user.email,
    } for user in users]
    return jsonify(users_list), 200



@app.route('/liboard/users/<int:user_id>', methods=['GET'])
@jwt_required()
def get_user_details(user_id):
    current_user = get_jwt_identity()
    if current_user['role'] != 'librarian':
        return jsonify({'error': 'Unauthorized'}), 403
    user = User.query.get_or_404(user_id)
    rental_count = RentalRequest.query.filter_by(user_id=user.id, status='accepted').count()
    user_details = {'id': user.id,'full_name': user.full_name,'username': user.username,'email': user.email,'role': user.role,'rental_count': rental_count,}
    return jsonify(user_details), 200




@app.route('/liboard/users/<int:user_id>/disable', methods=['POST'])
@jwt_required()
def disable_user(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404
    
    if not user.is_active:
        return jsonify({"error": "User is already disabled"}), 400 
    user.is_active = False
    db.session.commit()
    return jsonify({"message": "User access disabled successfully"}), 200



@app.route('/liboard/rental_hist', methods=['GET'])
@jwt_required()
def get_rental_history():
    current_user = get_jwt_identity()
    if current_user['role'] != 'librarian':
        return jsonify({'error': 'Unauthorized'}), 403
    rental_requests = RentalRequest.query.all()
    history_list = [{
        'id': req.id,
        'user': req.user.full_name,
        'book': req.book.title,
        'status': req.status,
        'date_requested': req.date_requested.strftime('%d-%m-%Y'),
        'date_returned': req.date_returned.strftime('%d-%m-%Y') if req.date_returned else 'N/A'
    } for req in rental_requests]
    return jsonify({'rental_hist': history_list}), 200



@app.route('/liboard/on_rent', methods=['GET'])
@jwt_required()
def get_books_on_rent():
    current_user = get_jwt_identity()
    if current_user['role'] != 'librarian':
        return jsonify({'error': 'Unauthorized'}), 403
    rental_requests = RentalRequest.query.filter_by(status='accepted').all()
    books_on_rent = []  
    for req in rental_requests:
        book = Book.query.get(req.book_id)
        if book:
            books_on_rent.append({
                'book_id': book.id,
                'image_url': book.image,
                'book_name': book.title,
                'username': User.query.get(req.user_id).username
            })
    return jsonify({'books_on_rent': books_on_rent}), 200



@app.route('/liboard/revoke_access/<int:book_id>', methods=['POST'])
@jwt_required()
def revoke_access(book_id):
    current_user = get_jwt_identity()
    if current_user['role'] != 'librarian':
        return jsonify({'error': 'Unauthorized'}), 403
    rental_request = RentalRequest.query.filter_by(book_id=book_id, status='accepted').first()
    if not rental_request:
        return jsonify({'error': 'Rental request not found'}), 404
    rental_request.status = 'returned'
    book = Book.query.get(book_id)
    if book:
        book.is_available = True
    db.session.commit()
    return jsonify({'message': 'Access revoked successfully'}), 200



@app.route('/uboard', methods=['GET'])
@jwt_required()
def get_available_books():
    current_user = get_jwt_identity()
    user = User.query.filter_by(username=current_user['username']).first()
    available_books = Book.query.filter_by(is_available=True).all()
    
    books_list = [{
        'id': book.id,
        'title': book.title,
        'author': book.author,
        'genre': book.genre.name,
        'image': book.image,
        'is_available': book.is_available
    } for book in available_books]  
    return jsonify({'books': books_list}), 200



@app.route('/uboard/book/<int:book_id>', methods=['GET'])
@jwt_required()
def get_book_details(book_id):    
    book = Book.query.get_or_404(book_id)
    
    book_details = {
        'id': book.id,
        'title': book.title,
        'author': book.author,
        'genre': book.genre.name if book.genre else 'Unknown',
        'image': book.image,
        'content': book.content,
        'is_available': book.is_available
    }
    return jsonify({'book': book_details}), 200



@app.route('/uboard/rent/<int:book_id>', methods=['POST'])
@jwt_required()
def rent_book(book_id):
    current_user = get_jwt_identity()
    user = User.query.filter_by(username=current_user['username']).first()
    book = Book.query.get_or_404(book_id)
    if not book.is_available:
        return jsonify({'error': 'Book is not available'}), 400
    active_rentals = RentalRequest.query.filter_by(user_id=user.id, status='accepted').count()
    pending_requests = RentalRequest.query.filter_by(user_id=user.id, status='pending').count()
    # Check if the user has already rented 5 books
    total_requests = active_rentals + pending_requests
    if total_requests >= 5:
        return jsonify({'error': 'You can only rent up to 5 books at a time'}), 400
    # Create a new rental request
    rental_request = RentalRequest(user_id=user.id, book_id=book_id, status='pending')
    book.is_available = False 
    db.session.add(rental_request)
    db.session.commit()
    return jsonify({'message': 'Rental request submitted successfully'}), 201



@app.route('/uboard/mybooks', methods=['GET'])
@jwt_required()
def get_my_books():
    current_user = get_jwt_identity()
    user = User.query.filter_by(username=current_user['username']).first()
    rental_requests = RentalRequest.query.filter_by(user_id=user.id, status='accepted').all()
    my_books = []
    for request in rental_requests:
        book = Book.query.get(request.book_id)
        if book:
            my_books.append({
                'id': book.id,
                'title': book.title,
                'image': book.image,
                'author': book.author,
            }) 
    return jsonify({'books': my_books}), 200



@app.route('/uboard/return/<int:book_id>', methods=['POST'])
@jwt_required()
def return_book(book_id):
    current_user = get_jwt_identity()
    user = User.query.filter_by(username=current_user['username']).first()
    if not user:
        return jsonify({'message': 'User not found'}), 404
    rental_request = RentalRequest.query.filter_by(user_id=user.id, book_id=book_id).first()
    if not rental_request:
        return jsonify({'message': 'Rental request not found'}), 404
    if rental_request.status == 'returned':
        return jsonify({'message': 'Book already returned'}), 400
    book = Book.query.get(book_id)
    if not book:
        return jsonify({'message': 'Book not found'}), 404
    try:
        rental_request.status = 'returned'
        book.is_available = True
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'An error occurred during the return process'}), 500
    return jsonify({'message': 'Book returned successfully'}), 200



@app.route('/uboard/myrequests', methods=['GET'])
@jwt_required()
def user_rentals():
    current_user = get_jwt_identity()
    user = User.query.filter_by(username=current_user['username']).first()
    rental_requests = RentalRequest.query.filter_by(user_id=user.id).all()
    requests_list=[]
    for request in rental_requests:
        return_date = request.date_issued + timedelta(days=7)
        requests_list.append({
            'id': request.id,
            'book': request.book.title,
            'request_date': request.date_requested.strftime('%d-%m-%Y'),
            'return_date': return_date.strftime('%d-%m-%Y'),
            'status': request.status
        })
    return jsonify({'rental_requests': requests_list}), 200



@app.route('/uboard/myrequests/<int:request_id>/cancel', methods=['POST'])
@jwt_required()
def cancel_request(request_id):
    current_user = get_jwt_identity()
    user = User.query.filter_by(username=current_user['username']).first()
    rental_request = RentalRequest.query.filter_by(id=request_id, user_id=user.id).first()
    if not rental_request:
        return jsonify({'error': 'Request not found'}), 404
    if rental_request.status != 'pending':
        return jsonify({'error': 'Only pending requests can be cancelled'}), 400
    rental_request.status = 'cancelled'
    book = Book.query.get(rental_request.book_id)
    if book:
        book.is_available = True
    db.session.commit()
    return jsonify({'message': 'Request cancelled successfully'}), 200



@app.route('/uboard/update_profile', methods=['POST'])
@jwt_required()
def update_profile():
    current_user = get_jwt_identity()
    user = User.query.filter_by(username=current_user['username']).first()
    if not user:
        return jsonify({'error': 'User not found'}), 404
    data = request.json
    user.full_name = data.get('full_name', user.full_name)
    user.email = data.get('email', user.email)
    db.session.commit()
    return jsonify({'message': 'Profile updated successfully'}), 200



@app.route('/protected', methods=['GET'])
@jwt_required()
def protected():
    current_user = get_jwt_identity()
    return jsonify(logged_in_as=current_user), 200


@app.route('/liboard/export_rentals', methods=['POST'])
@jwt_required()
def export_rentals():
    current_user = get_jwt_identity()
    if current_user['role'] != 'librarian':
        return jsonify({'error': 'Unauthorized'}), 403
    task = export_rentals_task.apply_async()
    return jsonify({'task_id': task.id}), 200


@celery.task
def export_rentals_task():
    import csv
    from io import StringIO
    rentals = RentalRequest.query.all()
    output = StringIO()
    writer = csv.writer(output)
    writer.writerow(['Name', 'Content', 'Author', 'Date Issued', 'Return Date', 'Current User'])
    for rental in rentals:
        writer.writerow([
            rental.book.title,
            rental.book.content,
            rental.book.author,
            rental.date_requested.strftime('%d-%m-%Y'),
            rental.return_date.strftime('%d-%m-%Y') if rental.return_date else '',
            rental.user.username
        ])
    output.seek(0)
    output_filename = f'rentals_{datetime.now().strftime("%Y%m%d%H%M%S")}.csv'
    with open(os.path.join('static/exports', output_filename), 'w') as file:
        file.write(output.getvalue())
    output.close()
    return output_filename


if __name__ == '__main__':
    app.run(debug=True)

