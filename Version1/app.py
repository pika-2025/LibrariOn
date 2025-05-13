from flask import Flask, render_template, redirect, request, url_for,session
from models import db,Admin, User, Book, Genre, RentalRequest, EbookReturn, FeedBack
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
import os
import plotly.graph_objs as go


app=Flask(__name__, static_url_path='/static')
app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///library.db'
app.secret_key='22f3002119'
app.config['UPLOAD_FOLDER']='static'


db.init_app(app)


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET','POST'])
def login():
    if request.method=='POST':
        username=request.form['username']
        password=request.form['password']
        user = User.query.filter_by(username=username, password=password).first()
        if user:
            session['user_id']=user.id
            return redirect('/login/user_dashboard')
        else:
            return render_template('/wrong_user.html')
    return render_template('login.html')

@app.route('/register', methods=['GET','POST'])
def register():
    if request.method == 'POST':
        full_name=request.form['full_name']
        username = request.form['username']
        email = request.form['email']
        mob_num = request.form['mob_num']
        password = request.form['password']
        profile_photo = request.files['profile_photo']
        if profile_photo:
            filename=profile_photo.filename
            profile_photo_path=os.path.join(app.config['UPLOAD_FOLDER'], filename)
            profile_photo.save(profile_photo_path)
        else:
            profile_photo_path=None
        user = User(full_name=full_name, username=username,  email=email, mob_num=mob_num, password=password, profile_photo_path=profile_photo_path)
        db.session.add(user)
        db.session.commit()
        db.session.close()
        return redirect('/login')
    return render_template('register.html')

@app.route('/login/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form['email']
        user = User.query.filter_by(email=email).first()
        if user:
            new_password=request.form['new_password']
            user.password = new_password
            db.session.commit()
            return redirect(url_for('login'))
        else:
            return render_template('login.html')
    return render_template('forgot_password.html')

@app.route('/login/user_dashboard')
def user_dashboard():
    user_id = session.get('user_id')
    if user_id:
        user = User.query.filter_by(id=user_id).first()
        if user:
            fullname=user.full_name
            all_books = Book.query.filter_by(is_available=True).all()
    return render_template('user_dashboard.html', fullname = fullname,user=user, all_books = all_books)

@app.route('/search_user', methods=['POST', 'GET'])
def search_books_user():
    search_book = request.form['search_book']
    search_criteria = request.form['search_criteria']
    if search_criteria == 'title':
        books = Book.query.filter(Book.title.ilike(f'%{search_book}%'), Book.is_available==True).all()
    elif search_criteria == 'author':
        books = Book.query.filter(Book.author.ilike(f'%{search_book}%'), Book.is_available==True).all()
    elif search_criteria == 'genre':
        books = Book.query.filter(Book.genre.ilike(f'%{search_book}%'), Book.is_available==True).all()
    else:
        return redirect('/admin_dashboard')
    return render_template('searched_book_user.html', books=books, search_book=search_book, search_criteria=search_criteria)

@app.route('/rent_book/<int:book_id>')
def rent_book(book_id):
    user_id = session.get('user_id')
    user = User.query.get(user_id)
    if user is None:
        return redirect(url_for('login'))
    if len(user.books) >= 5:
        return redirect(url_for('user_dashboard'))
    book = Book.query.get(book_id)
    rental_request = RentalRequest(user_id=user_id, book_id=book_id)
    db.session.add(rental_request)
    db.session.commit()
    book.is_available= False
    db.session.commit()
    return redirect('/login/user_dashboard') 

@app.route('/buy_book/<int:book_id>')
def buy_book(book_id):
    return render_template('payment.html', book_id=book_id)

@app.route('/confirm_payment/<int:book_id>')
def confirm_payment(book_id):
    book=Book.query.get(book_id)
    return render_template('download.html', book=book)

@app.route('/my_books')
def my_books():
    user_id = session.get('user_id')
    if user_id:
        user = User.query.get(user_id)
        if user:
            books = db.session.query(Book, EbookReturn).filter_by(renter_id = user_id).join(EbookReturn).all()
            return render_template('my_books.html', user=user, books=books)
    return redirect('/login')

@app.route('/cancel_request/<int:request_id>')
def cancel_request(request_id):
    request = RentalRequest.query.get(request_id)
    if request:
        book = request.book
        if book:
            book.is_available = True
            db.session.delete(request)
            db.session.commit()
    return redirect('/rental_requests')



@app.route('/give_feedback/<int:book_id>', methods=['GET','POST'])
def give_feedback(book_id):
    user_id = session.get('user_id')
    if user_id:
        user = User.query.get(user_id)
        if user:
            if request.method == 'POST':
                feedback_text = request.form['feedback']
                rating = request.form['rating']
                feedback = FeedBack(book_id=book_id, user_id=user_id, feedback=feedback_text, rating=rating)
                db.session.add(feedback)
                db.session.commit()
                return redirect('/my_books')
            book = Book.query.get(book_id)
            return render_template('give_feedback.html', book=book)
    return redirect('/login')

@app.route('/see_feedbacks/<int:book_id>')
def see_feedbacks(book_id):
    book = Book.query.get(book_id)
    if book:
        feedbacks = FeedBack.query.filter_by(book_id=book_id).all()
        return render_template('see_feedbacks.html', book = book, feedbacks=feedbacks)
    return redirect('/login/user_dashboard')

@app.route('/return_book/<int:book_id>')
def return_book(book_id):
    book = Book.query.get(book_id)
    if book:
        book.is_available = True
        ebook_return = EbookReturn.query.filter_by(book_id=book_id).first()
        if ebook_return:
            db.session.delete(ebook_return)
            db.session.commit()
    return redirect(url_for('my_books'))



@app.route('/rental_requests')
def rental_requests():
    user_id = session.get('user_id')
    user = User.query.get(user_id)
    if user:
        rental_requests = user.rental_requests
        return render_template('request_status.html', rental_requests=rental_requests)
    return redirect('/login/user_dashboard')



@app.route('/user_profile')
def user_profile():
    user_id=session.get('user_id')
    user = User.query.get(user_id)
    return render_template('user_profile.html', user = user)

@app.route('/edit_user_profile', methods = ['GET','POST'])
def edit_user_profile():
    user_id = session.get('user_id')
    user = User.query.get(user_id)
    if request.method == 'POST':
        user.full_name = request.form.get('full_name')
        user.username = request.form.get('username')
        user.email = request.form.get('email')
        user.mob_num = request.form.get('mob_num')
        
        profile_photo = request.files['profile_photo']
        if profile_photo:
            profile_photo_path = os.path.join(app.config['UPLOAD_FOLDER'], profile_photo.filename)
            profile_photo.save(profile_photo_path)
            user.profile_photo_path = profile_photo_path
        db.session.commit()
        return redirect('/user_profile')
    return render_template('edit_user_profile.html', user=user)



@app.route('/admin_setup', methods = ['GET','POST'])
def admin_setup():
    admin = Admin.query.first()
    if admin:
        return redirect('/login/admin_login')
    if request.method == 'POST':
        full_name = request.form['full_name']
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        mob_num=request.form['mob_num']
        profile_photo=request.files['profile_photo']
        if profile_photo:
            filename = profile_photo.filename
            profile_photo_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            profile_photo.save(profile_photo_path)
        else:
            profile_photo_path = None
        admin = Admin(full_name=full_name,username=username, password=password, email=email, mob_num=mob_num, profile_photo_path=profile_photo_path)
        db.session.add(admin)
        db.session.commit()
        return redirect('/login/admin_login')
    return render_template('admin_setup.html')



def check_overdue_books():
    current_date = datetime.now()
    overdue_books = EbookReturn.query.filter(EbookReturn.return_date <=current_date).all()
    for books in overdue_books:
        book = Book.query.get(books.book_id)
        book.is_available=True
        db.session.delete(books)
    db.session.commit()

@app.route('/login/admin_login', methods=['GET','POST'])
def admin_login():
    if request.method=='POST':
        username = request.form['username']
        password = request.form['password']
        admin = Admin.query.filter_by(username = username, password = password).first()
        if admin:
            check_overdue_books()
            session['username'] = admin.username
            return redirect('/admin_dashboard')
        return render_template('wrong_user.html')
    admin_exists = Admin.query.first()
    if not admin_exists:
        return redirect('/admin_setup')
    return render_template('admin_login.html')


@app.route('/forgot_admin_password', methods = ['GET','POST'])
def forgot_admin_password():
    if request.method=='POST':
        username = request.form['username']
        user = Admin.query.get(username)
        if user:
            new_password = request.form['password']
            user.password = new_password
            db.session.commit()
            return redirect('/login/admin_login')
        else:
            return render_template('forgot_admin_password.html')       
    return render_template('forgot_admin_password.html')



@app.route('/admin_dashboard')
def ebook_requests():
    requests = RentalRequest.query.filter_by(status='Pending').all()
    return render_template('admin_dashboard.html', requests=requests)


@app.route('/search_admin', methods=['POST', 'GET'])
def search_books_admin():
    search_book = request.form['search_book']
    search_criteria = request.form['search_criteria']
    if search_criteria == 'title':
        books = Book.query.filter(Book.title.ilike(f'%{search_book}%'), Book.is_available==True).all()
    elif search_criteria == 'author':
        books = Book.query.filter(Book.author.ilike(f'%{search_book}%'), Book.is_available==True).all()
    elif search_criteria == 'genre':
        books = Book.query.filter(Book.genre.ilike(f'%{search_book}%'), Book.is_available==True).all()
    else:
        return redirect('/admin_dashboard')
    return render_template('searched_book_admin.html', books=books, search_book=search_book, search_criteria=search_criteria)



@app.route('/accept_rental_request/<int:request_id>')
def accept_rental_request(request_id):
    rental_request = RentalRequest.query.get(request_id)
    if rental_request:
        rental_request.status = 'Approved'
        rental_request.issued_date = datetime.now()
        return_date = datetime.now()+ timedelta(days=3)
        ebook_return = EbookReturn(user_id=rental_request.user_id, book_id=rental_request.book_id, return_date=return_date)
        db.session.add(ebook_return)
        db.session.commit()
        user = rental_request.user
        book = rental_request.book
        if user and book:
            book.renter_id = user.id
            db.session.commit()
    return redirect('/admin_dashboard')



@app.route('/reject_rental_request/<int:request_id>')
def reject_rental_request(request_id):
    rental_request = RentalRequest.query.get(request_id)
    if rental_request:
        rental_request.status = 'Rejected'
        book = rental_request.book
        if book:
            book.is_available = True
        db.session.commit()
    return redirect('/admin_dashboard')


@app.route('/issued_books')
def issued_books():
    issued_books = db.session.query(Book, User).join(User, Book.renter_id==User.id).join(RentalRequest, Book.id==RentalRequest.book_id).filter(Book.is_available==False, RentalRequest.status=='Approved').all()
    return render_template('issued_books.html', books = issued_books)

@app.route('/revoke_access/<int:book_id>')
def revoke_access(book_id):
    book = Book.query.get(book_id)
    if book:
        book.is_available = True
        book.renter_id = None
        db.session.commit()
        return redirect('/issued_books')



@app.route('/books')
def books():
    genres = Genre.query.all()
    return render_template('books.html', genres=genres)

@app.route('/add_genre', methods=['GET','POST'])
def add_genre():
    if request.method=='POST':
        name = request.form['genre']
        description = request.form['description']
        genre = Genre(genre=name, description=description)
        db.session.add(genre)
        db.session.commit()
        return redirect('/books')
    return render_template('add_genre.html')

@app.route('/edit_genre/<genre>', methods=['GET', 'POST'])
def edit_genre(genre):
    genre_obj = Genre.query.filter_by(genre=genre).first()
    if request.method == 'POST':
        new_genre_name = request.form['genre']
        new_description = request.form['description']
        genre_obj.genre = new_genre_name
        genre_obj.description = new_description
        db.session.commit()
        return redirect(url_for('books'))
    return render_template('edit_genre.html', genre=genre_obj)



@app.route('/books/<genre>')
def books_by_genre(genre):
    genre_entry = Genre.query.get(genre)
    if genre:
        books = Book.query.filter_by(genre=genre).all()
        return render_template('books_by_genre.html', genre=genre_entry, books=books)
    return redirect('/books')

@app.route('/add_book/<genre>', methods=['POST','GET'])
def add_book(genre):
    if request.method=='POST':
        preview = request.files['preview']
        if preview:
            filename = preview.filename
            preview_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            preview.save(preview_path)
        title = request.form['title']
        author = request.form['author']
        book_content = request.files['content']
        if book_content:
            filename = book_content.filename
            content = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            book_content.save(content)
        book = Book(title=title, author=author,genre=genre, preview_path=preview_path, Content=content)
        db.session.add(book)
        db.session.commit()
        return redirect('/books')
    return render_template('add_book.html', genre=genre)

@app.route('/edit_book/<int:book_id>', methods=['GET','POST'])
def edit_book(book_id):
    book = Book.query.get(book_id)
    if request.method=='POST':
        preview = request.files['preview']
        preview_path = os.path.join(app.config['UPLOAD_FOLDER'], preview.filename)
        preview.save(preview_path)
        book.preview_path = preview_path
        book.title = request.form['title']
        book.author = request.form['author']
        content = request.files['content']
        content_path = os.path.join(app.config['UPLOAD_FOLDER'], content.filename)
        content.save(content_path)
        book.Content = content_path  
        db.session.commit()
        return redirect(url_for('books_by_genre',genre=book.genre))
    return render_template('edit_book.html',book=book)



@app.route('/user_list')
def user_list():
    users=User.query.all()
    return render_template('user_table.html', users=users)

@app.route('/user_details/<int:user_id>')
def user_details(user_id):
    user = User.query.get(user_id)
    if user:
        user_books = user.books
        genre_count = {}
        for book in user_books:
            genre = book.genre
            genre_count[genre] = genre_count.get(genre,0) +1
        x_values = list(genre_count.keys())
        y_values = list(genre_count.values())
        scatter_pot = go.Figure(data=[go.Scatter(x=x_values, y=y_values, mode='markers')])
        scatter_pot.update_layout(title = 'Number of Books in each Genre', xaxis_title = 'Genre', yaxis_title = 'Number of Books')
        plot_html = scatter_pot.to_html(full_html=False)
        return render_template('user_details.html', user = user, plot=plot_html)
    return redirect('/user_list')


@app.route('/stats')
def stats():
    section_distribution = db.session.query(Genre.genre, db.func.count(Book.id)).join(Genre).group_by(Genre.genre).all()
    section_names = [sections[0] for sections in section_distribution]
    book_counts = [books[1] for books in section_distribution]
    pie_chart = go.Figure(data = [go.Pie(labels=section_names, values=book_counts)])
    pie_chart.update_layout(title='Section Distribution')
    plot_html = pie_chart.to_html(full_html=False)
    books=Book.query.all()
    data = []
    for book in books:
        request_count = RentalRequest.query.filter_by(book_id=book.id).count()
        data.append({'book_name':book.title, 'request_count':request_count})
    book_names = [entry['book_name'] for entry in data]
    requests_counts = [entry['request_count'] for entry in data]
    line_graph = go.Figure(data=[go.Scatter(x=book_names, y=requests_counts)])
    line_graph.update_layout(title='Total Number of Requets per Book', xaxis_title ='Book', yaxis_title='Number of Requests')
    graph_html = line_graph.to_html(full_html=False)
    return render_template('stats.html', plot=plot_html, graph=graph_html)



@app.route('/view_profile')
def view_profile():
    username = session.get('username')
    admin=Admin.query.get(username)
    return render_template('admin_profile.html',admin=admin)

@app.route('/update_admin', methods = ['GET','POST'])
def update_admin():
    username = session.get('username')
    admin = Admin.query.get(username)
    if request.method == 'POST':
        admin.full_name = request.form.get('full_name')
        admin.username = request.form.get('username')
        admin.email = request.form.get('email')
        admin.mob_num = request.form.get('mob_num')    
        profile_photo = request.files['profile_photo']
        if profile_photo:
            profile_photo_path = os.path.join(app.config['UPLOAD_FOLDER'], profile_photo.filename)
            profile_photo.save(profile_photo_path)
            admin.profile_photo_path = profile_photo_path
        db.session.commit()
        return redirect('/view_profile')
    return render_template('update_admin.html', admin=admin)

@app.route('/change_admin_password', methods = ['GET', 'POST'])
def change_admin_password():
    username = session.get('username')
    admin = Admin.query.get(username)
    if request.method == 'POST':
        current_password = request.form.get('current_password')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')
        if admin.password != current_password:
            return redirect('/change_admin_password')
        if new_password !=confirm_password:
            return redirect('/change_admin_password')
        admin.password = new_password
        db.session.commit()
        return redirect('/view_profile')
    return render_template('change_admin_password.html')

  
@app.route('/logout')
def logout():
    if 'user_id' in session:
        session.pop('user_id')
    elif 'username' in session:
        session.pop('username')
    return redirect('/')

if __name__=='__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
