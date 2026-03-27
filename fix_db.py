import db

mydb = db.get_db_connection()
cursor = mydb.cursor()

cursor.execute('DESCRIBE tasks')
columns = [row[0] for row in cursor.fetchall()]
print(f"Existing columns: {columns}")

if 'due_date' not in columns:
    cursor.execute("ALTER TABLE tasks ADD COLUMN due_date date NOT NULL DEFAULT '2026-01-01'")
    print("Added due_date")

if 'due_time' not in columns:
    cursor.execute("ALTER TABLE tasks ADD COLUMN due_time time NOT NULL DEFAULT '00:00:00'")
    print("Added due_time")

if 'recurring' not in columns:
    cursor.execute("ALTER TABLE tasks ADD COLUMN recurring varchar(20) NOT NULL DEFAULT 'once'")
    print("Added recurring")

if 'priority' not in columns:
    cursor.execute("ALTER TABLE tasks ADD COLUMN priority varchar(15) NOT NULL DEFAULT 'medium'")
    print("Added priority")

mydb.commit()
mydb.close()
print("Database schema fixed successfully!")
