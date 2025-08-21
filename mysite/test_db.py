import sqlite3

DB = "beauty.db"

conn = sqlite3.connect(DB)
cur = conn.cursor()

print("=== Записи клиентов ===")
for row in cur.execute("SELECT * FROM appointments"):
    print(row)

print("\n=== Расписание мастера ===")
for row in cur.execute("SELECT * FROM schedule"):
    print(row)

conn.close()
