import sqlite3

DB = "beauty.db"

conn = sqlite3.connect(DB)

# Преобразуем текстовые даты в DATE
conn.execute("""
    CREATE TABLE IF NOT EXISTS appointments_new (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        phone TEXT,
        service TEXT,
        date DATE,
        time TEXT
    )
""")

conn.execute("""
    CREATE TABLE IF NOT EXISTS schedule_new (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date DATE,
        time TEXT,
        status TEXT,
        UNIQUE(date, time)
    )
""")

# Переносим данные
conn.execute("""
    INSERT INTO appointments_new (id, name, phone, service, date, time)
    SELECT id, name, phone, service, date(date), time FROM appointments
""")

conn.execute("""
    INSERT INTO schedule_new (id, date, time, status)
    SELECT id, date(date), time, status FROM schedule
""")

conn.commit()

# Переименовываем таблицы
conn.execute("ALTER TABLE appointments RENAME TO appointments_old")
conn.execute("ALTER TABLE appointments_new RENAME TO appointments")

conn.execute("ALTER TABLE schedule RENAME TO schedule_old")
conn.execute("ALTER TABLE schedule_new RENAME TO schedule")

conn.commit()
conn.close()
