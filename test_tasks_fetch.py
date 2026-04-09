import db
mydb = db.get_db_connection()
cursor = mydb.cursor()
cursor.execute("SELECT task_id, user_id, task_title, task_description, due_date, due_time, recurring, priority, status, created_date FROM tasks WHERE user_id=4 ORDER BY due_date ASC, due_time ASC")
rows = cursor.fetchall()
print("ROWS FETCHED:", rows)
task_list = []
for t in rows:
    try:
        task_list.append({
            'task_id':     t[0],
            'user_id':     t[1],
            'title':       t[2] or '',
            'description': t[3] if t[3] and t[3] != 'None' else '',
            'date':        str(t[4]) if t[4] else '',
            'time':        str(t[5]) if t[5] else '',
            'recurring':   t[6] or 'once',
            'priority':    t[7] if t[7] and t[7] != 'None' else 'medium',
            'status':      t[8] or 'pending',
            'createdAt':   str(t[9]) if t[9] else ''
        })
    except Exception as e:
        print("ERROR ON ROW", t, e)
import json
print(json.dumps(task_list, indent=2))
