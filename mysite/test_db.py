import sqlite3

DB = "beauty.db"


def show_tables():
    """Показать список таблиц в БД"""
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cur.fetchall()
    conn.close()
    print("Список таблиц:")
    for t in tables:
        print("-", t[0])


def show_structure(table_name: str):
    """Показать структуру таблицы"""
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    cur.execute(f"PRAGMA table_info({table_name});")
    columns = cur.fetchall()
    conn.close()

    print(f"\nСтруктура таблицы {table_name}:")
    for col in columns:
        print(f"- {col[1]} ({col[2]})")


def show_data(table_name: str, limit: int = 10):
    """Показать данные таблицы (первые N строк)"""
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    cur.execute(f"SELECT * FROM {table_name} LIMIT {limit};")
    rows = cur.fetchall()
    conn.close()

    print(f"\nДанные из таблицы {table_name}:")
    for row in rows:
        print(row)


if __name__ == "__main__":
    # Пример использования
    show_tables()
    show_structure("appointments")
    show_data("appointments")
    show_structure("schedule")
    show_data("schedule")
