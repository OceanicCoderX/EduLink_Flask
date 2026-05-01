# ============================================================
# db.py — Database Connection
# Yeh function har route file mein import hoga
# ============================================================

import mysql.connector
from config import DB_HOST, DB_PORT, DB_USER, DB_PASSWORD, DB_NAME, DB_SSL_DISABLED


def get_db_connection():
    """
    Ek naya DB connection return karta hai.
    Use karo: mydb = get_db_connection()
    Kaam ke baad: mydb.close()
    """
    mydb = mysql.connector.connect(
        host=DB_HOST,
        port=DB_PORT,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME,
        ssl_disabled=DB_SSL_DISABLED,   # Local ke liye True, Aiven ke liye False
        use_pure=True
    )
    return mydb