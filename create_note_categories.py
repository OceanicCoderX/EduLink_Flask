"""
Migration: create note_categories table
Run once: python create_note_categories.py
"""
from db import get_db_connection

DEFAULT_CATEGORIES = [
    ('General',   '#8898aa'),
    ('Physics',   '#5e72e4'),
    ('Chemistry', '#2dce89'),
    ('Math',      '#fb6340'),
    ('Biology',   '#11cdef'),
    ('Coding',    '#f5365c'),
]

mydb   = get_db_connection()
cursor = mydb.cursor()

# 1. Create table
cursor.execute("""
CREATE TABLE IF NOT EXISTS note_categories (
    cat_id     INT AUTO_INCREMENT PRIMARY KEY,
    user_id    INT NOT NULL,
    name       VARCHAR(60) NOT NULL,
    color      VARCHAR(20) DEFAULT '#5e72e4',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY uq_user_cat (user_id, name)
)
""")
mydb.commit()
print("✅ note_categories table created (or already existed).")

cursor.close()
mydb.close()
print("Done.")
