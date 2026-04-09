import mysql.connector
import config
import json
import datetime

def myconverter(o):
    if isinstance(o, datetime.datetime) or isinstance(o, datetime.date) or isinstance(o, datetime.timedelta):
        return o.__str__()

db = mysql.connector.connect(host=config.DB_HOST, user=config.DB_USER, password=config.DB_PASSWORD, database=config.DB_NAME)
cursor = db.cursor(dictionary=True)
cursor.execute('SELECT * FROM tasks')
rows = cursor.fetchall()

print(json.dumps(rows, default=myconverter, indent=2))
