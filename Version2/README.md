# Library Management System – Version 2

This is the second version of my Library Management System project. In this version, I have implemented a modern web application using **Flask** for the backend and **JavaScript** modules for the frontend, providing a more interactive and dynamic user experience.

---

## Features

- **User & Admin Roles:** Secure registration, login, and role-based access.
- **Book & Genre Management:** Add, edit, delete, and view books and genres.
- **Rental Workflow:** Request, approve, reject, and return books; view rental history.
- **Profile Management:** Update user/admin profiles.
- **RESTful API:** Backend endpoints for all major actions, consumed by JavaScript frontend.
- **Dynamic Frontend:** All user interactions and page updates handled with JavaScript modules.
- **Modular Codebase:** Organized JavaScript files for components, pages, and utilities.
- **File Uploads:** Manage profile pictures and book images.
- **Responsive UI:** Styled with CSS for a modern look.

---


## Getting Started

### 1. Clone the Repository

- `git clone https://github.com/LibrariOn.git`
- `cd Version2`

### 2. Set Up a Virtual Environment

`python -m venv venv`

- On Windows:
`venv\Scripts\activate`

- On Mac/Linux:
`source venv/bin/activate`


### 3. Install Dependencies

`pip install -r requirements.txt`

### 4. Run the Application

- `python app.py`

- Visit [http://127.0.0.1:5000](http://127.0.0.1:5000) in your browser.

---

## Usage

- **Login/Register:** Access as user or admin.
- **Dashboard:** Manage books, genres, rentals, and profiles.
- **Dynamic Pages:** All navigation and updates are handled by JavaScript modules for a seamless user experience.
- **Admin Features:** User management, viewing rental stats, and exporting data.

---

## Notes

- **Frontend:** All major UI logic is handled by JavaScript files in `static/pages/` and `static/components/`.
- **Backend:** Flask serves API endpoints and renders initial HTML templates.
- **No sensitive data:** Do not commit actual credentials or private data.
- **For demonstration:** This project is for educational/demo purposes.

---

## Author

Piyush Kant  
