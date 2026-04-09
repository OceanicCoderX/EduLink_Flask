# ============================================================
# hash_passwords.py — One-time password migration
# Run ONCE: python hash_passwords.py
# After running, all passwords will be bcrypt hashed
# ============================================================

from werkzeug.security import generate_password_hash
from db import get_db_connection

def migrate_passwords():
    mydb   = get_db_connection()
    cursor = mydb.cursor()

    # Get all users with plain-text passwords
    # Plain text passwords don't start with 'pbkdf2:' or 'scrypt:'
    cursor.execute("SELECT user_id, password FROM users")
    users = cursor.fetchall()

    updated = 0
    skipped = 0

    for user_id, pwd in users:
        # Skip already-hashed passwords
        if pwd.startswith('pbkdf2:') or pwd.startswith('scrypt:'):
            skipped += 1
            continue

        # Hash the plain text password
        hashed = generate_password_hash(pwd)
        cursor.execute(
            "UPDATE users SET password=%s WHERE user_id=%s",
            (hashed, user_id)
        )
        updated += 1
        print(f"  ✅ User {user_id} password hashed")

    mydb.commit()
    cursor.close()
    mydb.close()

    print(f"\n Done! {updated} passwords hashed, {skipped} already hashed.")


if __name__ == '__main__':
    print("🔐 EduLink — Password Migration Tool")
    print("=" * 40)
    confirm = input("This will hash all plain-text passwords. Continue? (yes/no): ")
    if confirm.lower() == 'yes':
        migrate_passwords()
    else:
        print("Aborted.")
