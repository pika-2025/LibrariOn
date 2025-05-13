from app import celery, app
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from celery import shared_task
from models import *
from datetime import datetime, timedelta

@shared_task(ignore_result=False)
def send_email(to,subject,body='', report_html=None):
    msg = MIMEMultipart('alternative')
    msg['Subject'] = subject
    msg['From'] = 'pikant2024@outlook.com'
    msg['To'] = to
    
    part1 = MIMEText(body, 'plain')
    msg.attach(part1)
    if report_html:
        part2 = MIMEText(report_html, 'html')
        msg.attach(part2)
    
    # msg.attach(part1)
    # msg.attach(part2)
    with smtplib.SMTP('smtp-mail.outlook.com', 587) as server:
        server.starttls()
        server.login('pikant2024@outlook.com','Pi@010303')
        server.sendmail(msg['From'],msg['To'],msg.as_string())
    return None

@celery.task()
def daily_reminder():
    with app.app_context():
        # Calculate the date for 1 day from now
        reminder_date = datetime.utcnow().date() + timedelta(days=1)
        
        # Calculate the target date (7 days from date_issued)
        target_date = datetime.utcnow().date() - timedelta(days=6)

        # Query rental requests where the book is due tomorrow
        rental_requests = RentalRequest.query.filter(
            db.func.date(RentalRequest.date_issued) == target_date
        ).all()
        
        for request in rental_requests:
            user = request.user
            book = request.book
            subject = f"Reminder: Upcoming Book Return - {book.title}"

            body = f'Dear {user.full_name},\n\nThis is a reminder to return the book "{book.title}" by {request.return_date.strftime("%Y-%m-%d")}. Please return it on time to avoid any late fees.\n\nThank you!'
            send_email.delay(to=user.email, subject=subject, body=body)

from datetime import datetime, timedelta
from flask import render_template

@celery.task()
def send_monthly_activity_report():
    with app.app_context():
        # Calculate the start and end dates of the previous month
        today = datetime.utcnow().date()
        first_day_of_this_month = today.replace(day=1)
        last_day_of_last_month = first_day_of_this_month - timedelta(days=1)
        first_day_of_last_month = last_day_of_last_month.replace(day=1)

        # Query database for activities in the last month
        new_users = User.query.filter(User.date_created.between(first_day_of_last_month, last_day_of_last_month)).count()
        books_rented = RentalRequest.query.filter(RentalRequest.date_issued.between(first_day_of_last_month, last_day_of_last_month)).count()
        books_returned = RentalRequest.query.filter(RentalRequest.date_requested.between(first_day_of_last_month, last_day_of_last_month), RentalRequest.status == 'returned').count()

        # Render the report (you could also format this as a plain text email or use an HTML template)
        report_html = render_template('monthly_report.html', new_users=new_users, books_rented=books_rented, books_returned=books_returned, start_date=first_day_of_last_month, end_date=last_day_of_last_month)

        # Send the email to the librarian
        subject = "Monthly Activity Report"
        body = (
            f"Dear Librarian,\n\n"
            f"Please find below the activity report for the period from {first_day_of_last_month.strftime('%Y-%m-%d')} to {last_day_of_last_month.strftime('%Y-%m-%d')}:\n\n"
            f"New Users: {new_users}\n"
            f"Books Rented: {books_rented}\n"
            f"Books Returned: {books_returned}\n\n"
            f"Thank you for managing the library's operations effectively.\n\n"
            f"Best regards,\n"
            f"Library System"
        )
        send_email.delay(to='librarian@example.com', subject=subject, body=body, report_html=report_html)
