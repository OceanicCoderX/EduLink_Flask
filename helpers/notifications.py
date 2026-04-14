# ============================================================
# helpers/notifications.py — Email + WhatsApp notifications
# Rule 5: Flask-Mail (email) + Twilio (WhatsApp)
# ============================================================

from config import (
    MAIL_SERVER, MAIL_PORT, MAIL_USE_TLS,
    MAIL_USERNAME, MAIL_PASSWORD, MAIL_DEFAULT_SENDER,
    TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN,
    TWILIO_WHATSAPP_FROM
)


# ── Email (Flask-Mail) ───────────────────────────────────────

def send_email(to_email: str, subject: str, body: str, app=None) -> bool:
    """
    Send an email via Flask-Mail.
    Usage:
        from helpers.notifications import send_email
        send_email('user@email.com', 'Task Due', 'Your task is due tomorrow!')
    """
    try:
        from flask_mail import Mail, Message
        from flask import current_app
        
        # Use current_app if no app instance is passed
        target_app = app or current_app
        mail = Mail(target_app)
        
        msg  = Message(subject=subject, recipients=[to_email], body=body,
                       sender=MAIL_DEFAULT_SENDER)
        mail.send(msg)
        return True
    except Exception as e:
        print(f"[Mail] Error sending email to {to_email}: {e}")
        return False


# ── WhatsApp (Twilio) ────────────────────────────────────────

def send_whatsapp(to_number: str, message: str) -> bool:
    """
    Send a WhatsApp message via Twilio Sandbox.
    to_number should be: '+91XXXXXXXXXX'
    Usage:
        send_whatsapp('+917558569152', 'Your task is due tomorrow!')
    """
    try:
        from twilio.rest import Client
        client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
        client.messages.create(
            from_=f'whatsapp:{TWILIO_WHATSAPP_FROM}',
            to=f'whatsapp:{to_number}',
            body=message
        )
        return True
    except Exception as e:
        print(f"[WhatsApp] Error sending to {to_number}: {e}")
        return False


# ── Smart Notification (respects user preference) ────────────

def notify_user(user_row: dict, subject: str, body: str, app=None) -> None:
    """
    Notify user based on their preferred channel.
    user_row needs: { email, whatsapp, notif_channel }
    """
    channel = user_row.get('notif_channel', 'email')

    if channel == 'email':
        send_email(user_row['email'], subject, body, app=app)

    elif channel == 'whatsapp':
        number = user_row.get('whatsapp', '')
        if number:
            # Add country code if not present
            if not number.startswith('+'):
                number = '+91' + number
            send_whatsapp(number, f"{subject}\n\n{body}")

    elif channel == 'both':
        send_email(user_row['email'], subject, body, app=app)
        number = user_row.get('whatsapp', '')
        if number:
            if not number.startswith('+'):
                number = '+91' + number
            send_whatsapp(number, f"{subject}\n\n{body}")

    # 'none' → do nothing
