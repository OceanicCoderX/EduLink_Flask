import app

with app.app.test_client() as c:
    with c.session_transaction() as sess:
        sess['user_id'] = 1
    rv = c.get('/api/tasks')
    print("STATUS:", rv.status_code)
    try:
        data = rv.get_json()
        print("DATA_LENGTH:", len(data) if data else 0)
        if data:
            print("FIRST ROW:", data[0])
    except Exception as e:
        print("ERROR:", e)
        print("RAW RESPONSE:", rv.data)
