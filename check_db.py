import sys
from db import get_db_connection


def main():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        res = cursor.fetchone()
        print("DB connection OK ->", res)
    except Exception as e:
        print("DB connection FAILED ->", repr(e))
        sys.exit(1)
    finally:
        try:
            cursor.close()
        except Exception:
            pass
        try:
            conn.close()
        except Exception:
            pass


if __name__ == "__main__":
    main()
