# reset_schedule.py
import sqlite3

DB = "beauty.db"

conn = sqlite3.connect(DB)
cursor = conn.cursor()

# удалить таблицу
cursor.execute("DROP TABLE IF EXISTS schedule")

# пересоздать с UNIQUE(date, time)
cursor.execute("""
CREATE TABLE schedule (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT NOT NULL,
    time TEXT NOT NULL,
    status TEXT NOT NULL,
    UNIQUE(date, time)
)
""")

conn.commit()
conn.close()

print("Таблица schedule пересоздана!")
