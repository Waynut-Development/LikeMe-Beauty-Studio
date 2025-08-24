import sqlite3

DB = "beauty.db"


def clear_table(table_name: str):
    """Удалить все данные из таблицы"""
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    cur.execute(f"DELETE FROM {table_name};")
    conn.commit()
    conn.close()
    print(f"Таблица {table_name} очищена!")


def drop_table(table_name: str):
    """Удалить таблицу полностью"""
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    cur.execute(f"DROP TABLE IF EXISTS {table_name};")
    conn.commit()
    conn.close()
    print(f"Таблица {table_name} удалена!")


def reset_db():
    """Полностью очистить все таблицы (без удаления структуры)"""
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    cur.execute("DELETE FROM appointments;")
    cur.execute("DELETE FROM schedule;")
    conn.commit()
    conn.close()
    print("Все данные удалены из таблиц!")


def reset_and_reinit_db():
    """Удаляет таблицы и пересоздаёт структуру заново"""
    conn = sqlite3.connect(DB)
    cur = conn.cursor()

    # Удаляем таблицы
    cur.execute("DROP TABLE IF EXISTS appointments;")
    cur.execute("DROP TABLE IF EXISTS schedule;")

    # Создаём заново
    cur.execute("""
    CREATE TABLE appointments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        phone TEXT NOT NULL,
        service TEXT NOT NULL,
        date TEXT NOT NULL,
        time TEXT NOT NULL
    )
    """)

    cur.execute("""
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
    print("База полностью пересоздана!")


if __name__ == "__main__":
    # Примеры использования:
    #clear_table("appointments")
    #clear_table("schedule")
    # reset_db()
    # drop_table("appointments")
    # drop_table("schedule")
    # reset_and_reinit_db()
    pass
