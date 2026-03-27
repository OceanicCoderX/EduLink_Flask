"""Small helper to initialize the edulink database from SQL file.
Run: python init_db.py
It uses credentials from `config.py` (defaults set for XAMPP).
"""
import mysql.connector
from mysql.connector import errorcode
from config import DB_HOST, DB_PORT, DB_USER, DB_PASSWORD
import os

SQL_FILE = os.path.join(os.path.dirname(__file__), 'edulink_updated.sql')

def run_sql_file(path):
    with open(path, 'r', encoding='utf-8') as f:
        sql = f.read()

    try:
        conn = mysql.connector.connect(host=DB_HOST, port=DB_PORT, user=DB_USER, password=DB_PASSWORD)
        cursor = conn.cursor()
        # execute multi-statement SQL
        for result in cursor.execute(sql, multi=True):
            pass
        conn.commit()
        cursor.close()
        conn.close()
        print('Database initialized / updated successfully.')
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print('Access denied: check DB_USER/DB_PASSWORD in config.py')
        else:
            print('Database error:', err)


if __name__ == '__main__':
    if not os.path.exists(SQL_FILE):
        print('SQL file not found:', SQL_FILE)
    else:
        run_sql_file(SQL_FILE)
