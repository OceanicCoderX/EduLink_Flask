# ============================================================
# config.py — EduLink Configuration
# Yahan sab settings ek jagah hain
# ============================================================

# --- Database Config (XAMPP MySQL) ---
DB_HOST     = "localhost"
DB_PORT     = 3306
DB_USER     = "root"
DB_PASSWORD = ""          # XAMPP default = no password
DB_NAME     = "edulink"

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
MAIL_USERNAME       = ""   # your Gmail: example@gmail.com
MAIL_PASSWORD       = ""   # Gmail App Password (16-char)
MAIL_DEFAULT_SENDER = "EduLink <noreply@edulink.com>"

# --- Twilio Config (WhatsApp) ---
# To enable: sign up at twilio.com, get Sandbox credentials
TWILIO_ACCOUNT_SID    = ""   # Your Twilio Account SID
TWILIO_AUTH_TOKEN     = ""   # Your Twilio Auth Token
TWILIO_WHATSAPP_FROM  = "+14155238886"   # Twilio Sandbox number (default)
