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
UPLOAD_FOLDER   = "static/images"
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif"}
