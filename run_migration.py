import mysql.connector

db = mysql.connector.connect(host='localhost', user='root', password='', database='edulink')
cur = db.cursor()

stmts = [
    "ALTER TABLE classroom ADD COLUMN IF NOT EXISTS room_password VARCHAR(100) DEFAULT NULL AFTER room_notes",
    "ALTER TABLE classroom ADD COLUMN IF NOT EXISTS status ENUM('active','closed') NOT NULL DEFAULT 'active' AFTER room_password",
    "ALTER TABLE classroom ADD COLUMN IF NOT EXISTS total_minutes INT(11) NOT NULL DEFAULT 0 AFTER status",
    "ALTER TABLE room_members ADD COLUMN IF NOT EXISTS join_time DATETIME DEFAULT current_timestamp() AFTER join_date",
]

for s in stmts:
    try:
        cur.execute(s); db.commit()
        print(f"  OK: {s[:70]}")
    except Exception as e:
        print(f"  WARN: {e}")

cur.close(); db.close()
print("Done!")
