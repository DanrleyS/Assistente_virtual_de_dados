import sqlite3


def get_schema(db_path: str) -> str:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # pegar tabelas
    cursor.execute("""
        SELECT name FROM sqlite_master
        WHERE type='table'
        AND name NOT LIKE 'sqlite_%';
    """)

    tables = cursor.fetchall()

    schema_text = "Tabelas disponíveis:\n\n"

    for (table_name,) in tables:
        cursor.execute(f"PRAGMA table_info({table_name});")
        columns = cursor.fetchall()

        col_names = [col[1] for col in columns]
        schema_text += f"{table_name}({', '.join(col_names)})\n"

    conn.close()
    return schema_text