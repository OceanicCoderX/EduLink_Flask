import db

def fix_table():
    mydb = db.get_db_connection()
    cursor = mydb.cursor()
    
    # Check if table exists
    cursor.execute("SHOW TABLES LIKE 'uploaded_files'")
    if not cursor.fetchone():
        print("Creating 'uploaded_files' table...")
        cursor.execute("""
            CREATE TABLE uploaded_files (
                file_id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                file_name VARCHAR(255) NOT NULL,
                file_original VARCHAR(255) NOT NULL,
                file_type VARCHAR(50),
                file_path VARCHAR(500) NOT NULL,
                file_size BIGINT,
                shared TINYINT(1) DEFAULT 0,
                uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
            )
        """)
        mydb.commit()
        print("Table 'uploaded_files' created successfully!")
    else:
        print("Table 'uploaded_files' already exists.")
        
    cursor.close()
    mydb.close()

if __name__ == "__main__":
    fix_table()
