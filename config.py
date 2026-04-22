# ============================================================
# config.py — EduLink Configuration
# Yahan sab settings ek jagah hain
# ============================================================

import os



DB_HOST     = os.environ.get("DB_HOST", "edulink-db-oceaniccodderx.h.aivencloud.com")
DB_PORT     = int(os.environ.get("DB_PORT", 24980))
DB_USER     = os.environ.get("DB_USER", "avnadmin")
DB_PASSWORD = os.environ.get("DB_PASSWORD") # Set this in Render Dashboard
DB_NAME     = os.environ.get("DB_NAME", "edulink")

# --- Flask Config ---
SECRET_KEY  = "edulink_secret_key_change_this_in_production"

# --- File Upload Config ---
UPLOAD_FOLDER      = "static/uploads"
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "pdf", "docx", "pptx", "xlsx", "txt"}
MAX_CONTENT_LENGTH = 16 * 1024 * 1024   # 16 MB max upload size

# --- Flask-Mail Config (Gmail SMTP) ---
# To enable: set your Gmail credentials below
# Also enable "App Password" in your Google account settings
MAIL_SERVER         = "smtp.gmail.com"
MAIL_PORT           = 587
MAIL_USE_TLS        = True
MAIL_USERNAME       = "oceanprincess003@gmail.com"
MAIL_PASSWORD       = "aoyu qine cwfd aegq"
MAIL_DEFAULT_SENDER = "EduLink <oceanprincess003@gmail.com>"

# --- Twilio Config (WhatsApp) ---
# To enable: sign up at twilio.com, get Sandbox credentials
TWILIO_ACCOUNT_SID    = ""   # Your Twilio Account SID
TWILIO_AUTH_TOKEN     = ""   # Your Twilio Auth Token
TWILIO_WHATSAPP_FROM  = "+14155238886"   # Twilio Sandbox number (default)