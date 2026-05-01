import mysql.connector
from db import get_db_connection

def update_database():
    try:
        mydb = get_db_connection()
        cursor = mydb.cursor()

        # Drop unnecessary tables
        cursor.execute("DROP TABLE IF EXISTS post_likes;")
        cursor.execute("DROP TABLE IF EXISTS post_comments;")
        cursor.execute("DROP TABLE IF EXISTS posts;")
        
        # Create room_recordings table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS room_recordings (
            recording_id    INT AUTO_INCREMENT PRIMARY KEY,
            room_id         INT NOT NULL,
            recorded_by     INT NOT NULL,
            filename        VARCHAR(255) NOT NULL,
            file_path       VARCHAR(500) NOT NULL,
            duration_secs   INT DEFAULT 0,
            is_shared       TINYINT(1) DEFAULT 0,
            created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (room_id) REFERENCES classroom(room_id) ON DELETE CASCADE,
            FOREIGN KEY (recorded_by) REFERENCES users(user_id) ON DELETE CASCADE
        );
        """)

        mydb.commit()
        print("Database updated successfully.")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'mydb' in locals() and mydb.is_connected():
            mydb.close()

if __name__ == "__main__":
    update_database()
