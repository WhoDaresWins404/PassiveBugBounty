import sqlite3


class DatabaseManager:
    def __init__(self):
        # We'll use a persistent file in the current directory as local storage
        self.db_path = "scanner.db"

    def get_connection(self):
        return sqlite3.connect(self.db_path)

    def create_tables(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            # Table for tracking the overall scan status (jobs table)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS job (
                    id TEXT PRIMARY KEY,
                    target TEXT,
                    status TEXT,
                    progress INTEGER,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            # Table for storing the actual vulnerability reports
            cursor.execute(f"""
                CREATE TABLE IF NOT EXISTS finding (
                    title TEXT,
                    severity TEXT,
                    score INTEGER,
                    details TEXT
                )
            """)
            conn.commit()


dbmanager = DatabaseManager()

def init_db():
    dbmanager.create_tables()
