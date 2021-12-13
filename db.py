import sqlite3


class DB:
    def __init__(self, file_name="db.db"):
        self.file_name = file_name
        self.con = sqlite3.connect(self.file_name)

    def create_database(self):
        cur = self.con.cursor()
        cur.execute("""
        CREATE TABLE users (
            id INT NOT NULL PRIMARY KEY,
            d_id INT NOT NULL,
            d_name text,
            signup_date datetime,
        )
        """)

        self.con.commit()

    def check_db_empty(self) -> bool:
        cur = self.con.cursor()
        cur.execute("SELECT name FROM sqlite_master")
        rows = cur.fetchall()
        if len(rows) > 0:
            return False
        return True
