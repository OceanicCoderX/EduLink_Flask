import mysql.connector
import re

mydb = mysql.connector.connect(host='localhost', user='root', password='', database='edulink')
cursor = mydb.cursor()

with open('migrate_db.sql', 'r', encoding='utf-8') as f:
    raw = f.read()

# Strip comment lines then split on semicolons
lines = []
for line in raw.splitlines():
    stripped = line.strip()
    if not stripped.startswith('--'):
        lines.append(line)

sql_clean = '\n'.join(lines)

# Split on semicolons and drop empty
statements = [s.strip() for s in sql_clean.split(';') if s.strip()]

print(f'Found {len(statements)} statements to execute.\n')

errors = []
for i, stmt in enumerate(statements):
    try:
        cursor.execute(stmt)
        mydb.commit()
        preview = stmt.replace('\n', ' ').strip()[:80]
        print(f'  OK  [{i+1}/{len(statements)}]: {preview}')
    except mysql.connector.Error as e:
        err_msg = f'  !!  [{i+1}/{len(statements)}]: {e}'
        print(err_msg)
        errors.append(err_msg)
        mydb.rollback()

print()
if errors:
    print(f'{len(errors)} warning(s) — likely columns/tables that already existed:')
    for e in errors:
        print(e)
else:
    print('All statements executed without errors!')

cursor.close()
mydb.close()
print('\nMigration complete!')
