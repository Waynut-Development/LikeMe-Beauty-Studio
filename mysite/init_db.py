import sqlite3

DB = "beauty.db"

def init_db():
    conn = sqlite3.connect(DB)
    cur = conn.cursor()

    # appointments
    cur.execute("""
    CREATE TABLE IF NOT EXISTS appointments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        phone TEXT NOT NULL,
        service TEXT NOT NULL,
        date TEXT NOT NULL,
        time TEXT NOT NULL
    )
    """)

    # schedule
    cur.execute("""
    CREATE TABLE IF NOT EXISTS schedule (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date TEXT NOT NULL,
        time TEXT NOT NULL,
        status TEXT NOT NULL,
        UNIQUE(date, time) -- 🔑 ключ для ON CONFLICT
    )
    """)

    conn.commit()
    conn.close()
    print("База инициализирована!")

if __name__ == "__main__":
    init_db()


