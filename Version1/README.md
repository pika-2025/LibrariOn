# Library Management System – Version 1

A web-based Library Management System built using **Flask** and **SQLAlchemy**. This version uses server-side rendering with HTML templates (no JavaScript logic) and provides basic library functionalities for both users and administrators.

---

## Features

- **User Registration & Login:** Secure registration and login for users and admins.
- **Book Management:** Add, edit, search, rent, buy, and return books.
- **Genre Management:** Add, edit, and view genres.
- **Rental Requests:** Users can request to rent books; admins can approve or reject requests.
- **Profile Management:** Update user/admin profiles and upload profile photos.
- **Feedback System:** Users can leave feedback and ratings for books.
- **Statistics & Visualizations:** Admins can view usage statistics (via Plotly).
- **Session Management:** Secure session handling.
- **File Uploads:** Profile photos and book-related files.
- **Responsive UI:** Organized with HTML templates and static styles.

---

## Getting Started

### 1. Clone the Repository
- git clone https://github.com/pika-2025/LibrariOn.git
- cd Version1

### 2. Set Up a Virtual Environment (Recommended)
`python -m venv venv`

- On Windows:
`venv\Scripts\activate`

- On Mac/Linux:
`source venv/bin/activate`

### 3. Install Dependencies
- Flask
- Flask-SQLAlchemy
- plotly


### 4. Run the Application
`python app.py`


Visit [http://127.0.0.1:5000](http://127.0.0.1:5000) in your browser.

---

## Usage

- **Home Page:** Access the main dashboard.
- **Register/Login:** Create a new account or log in as a user/admin.
- **Dashboard:** Manage books, genres, rentals, and feedback.
- **Admin Features:** Manage users, books, genres, and view statistics.

---

## Data Models

Defined in `models.py` using SQLAlchemy:

- **Admin:** Library administrator with profile and credentials.
- **User:** Library user with profile and credentials.
- **Book:** Book details, availability, and content.
- **Genre:** Book categories.
- **RentalRequest:** Book rental requests and status.
- **EbookReturn:** Book return records.
- **FeedBack:** User feedback and ratings.

---

## Notes

- **Database:** Uses SQLite (`library.db`), auto-created on first run.
- **File Uploads:** Stored in the `static/` directory.
- **No JavaScript:** All logic is handled server-side.
- **Security:** For learning/demo purposes; not production-hardened.

---

## Author

Piyush Kant 
