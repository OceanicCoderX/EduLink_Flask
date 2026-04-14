import os
import sys

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from flask import Flask
from flask_mail import Mail, Message
from config import (
    MAIL_SERVER, MAIL_PORT, MAIL_USE_TLS,
    MAIL_USERNAME, MAIL_PASSWORD, MAIL_DEFAULT_SENDER
)

def test_email():
    app = Flask(__name__)
    app.config['MAIL_SERVER'] = MAIL_SERVER
    app.config['MAIL_PORT'] = MAIL_PORT
    app.config['MAIL_USE_TLS'] = MAIL_USE_TLS
    app.config['MAIL_USERNAME'] = MAIL_USERNAME
    app.config['MAIL_PASSWORD'] = MAIL_PASSWORD
    app.config['MAIL_DEFAULT_SENDER'] = MAIL_DEFAULT_SENDER

    mail = Mail(app)

    with app.app_context():
        try:
            print(f"Attempting to send test email to {MAIL_USERNAME}...")
            msg = Message(
                "EduLink Connection Test",
                recipients=[MAIL_USERNAME],
                body="Congratulations! Your EduLink email notification system is now active.\n\nAll rules (Welcome, Daily Tasks, Chat, OTP) have been implemented successfully."
            )
            mail.send(msg)
            print("Success! Test email sent.")
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    test_email()
