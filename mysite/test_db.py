import sqlite3
import os

DB = "beauty.db"

def get_connection():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn

def check_tables():
    conn = get_connection()
    cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [row["name"] for row in cursor.fetchall()]
    print("📋 Таблицы в базе:", tables)
    conn.close()

def test_appointments():
    conn = get_connection()
    print("\n--- Тест таблицы appointments ---")
    # Вставка
    conn.execute("""
        INSERT INTO appointments (name, phone, service, date, time)
        VALUES (?, ?, ?, ?, ?)
    """, ("Иван", "+79998887766", "Стрижка", "2025-08-24", "10:00"))
    conn.commit()
    # Чтение
    rows = conn.execute("SELECT * FROM appointments").fetchall()
    for row in rows:
        print(dict(row))
    conn.close()

def test_schedule():
    conn = get_connection()
    print("\n--- Тест таблицы schedule ---")
    # Вставка расписания
    conn.execute("""
        INSERT INTO schedule (date, time, status)
        VALUES (?, ?, ?)
        ON CONFLICT(date, time) DO UPDATE SET status=excluded.status
    """, ("2025-08-24", "09:00", "busy"))
    conn.commit()
    # Чтение
    rows = conn.execute("SELECT * FROM schedule").fetchall()
    for row in rows:
        print(dict(row))
    conn.close()

if __name__ == "__main__":
    if not os.path.exists(DB):
        print(f"❌ База {DB} не найдена. Сначала создай её через init_db.py")
    else:
        check_tables()
        test_appointments()
        test_schedule()
