from db import get_db_connection

def migrate():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Add status to group_members
        print("Checking group_members table...")
        cursor.execute("DESCRIBE group_members")
        columns = [r[0] for r in cursor.fetchall()]
        if 'status' not in columns:
            print("Adding 'status' to group_members...")
            cursor.execute("ALTER TABLE group_members ADD COLUMN status ENUM('pending', 'approved') DEFAULT 'approved'")
            conn.commit()
            print("Status column added successfully.")
        else:
            print("Status column already exists.")

        cursor.close()
        conn.close()
        print("Migration complete.")
    except Exception as e:
        print(f"Error during migration: {e}")

if __name__ == "__main__":
    migrate()
