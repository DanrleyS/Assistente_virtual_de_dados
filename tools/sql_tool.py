import sqlite3
import pandas as pd


class SQLTool:
    def __init__(self, db_path: str):
        self.db_path = db_path

    def run(self, query: str):
        try:
            conn = sqlite3.connect(self.db_path)

            df = pd.read_sql_query(query, conn)

            conn.close()

            return {
                "success": True,
                "data": df,
                "rows": len(df),  # 🔥 importante
                "error": None
            }

        except Exception as e:
            return {
                "success": False,
                "data": None,
                "rows": 0,
                "error": str(e)
            }