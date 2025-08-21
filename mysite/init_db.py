import sqlite3

def init_db():
    conn = sqlite3.connect("beauty.db")
    cur = conn.cursor()

    # Таблица записей клиентов
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

    # Таблица расписания
    cur.execute("""
    CREATE TABLE IF NOT EXISTS schedule (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date TEXT NOT NULL,
        time TEXT NOT NULL,
        status TEXT NOT NULL CHECK(status IN ('free','busy','off'))
    )
    """)

    conn.commit()
    conn.close()
    print("База данных инициализирована!")

if __name__ == "__main__":
    init_db()
