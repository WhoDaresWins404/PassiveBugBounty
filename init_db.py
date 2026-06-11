import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

def init_db():
    conn = psycopg2.connect(os.getenv("DATABASE_URL"))
    cur = conn.cursor()
    
    # Create tables
    cur.execute("""
    CREATE TABLE IF NOT EXISTS sessions (
        id SERIAL PRIMARY KEY,
        target TEXT NOT NULL,
        start_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        end_time TIMESTAMP,
        status TEXT CHECK (status IN ('running', 'completed', 'failed')) DEFAULT 'running'
    );

    -- ✅ Safe for all PostgreSQL versions:
    DO $$
    BEGIN
        IF NOT EXISTS (
            SELECT 1 FROM pg_type WHERE typname = 'event_type'
        ) THEN
            CREATE TYPE event_type AS ENUM ('request', 'response');
        END IF;
    END $$;

    CREATE TABLE IF NOT EXISTS events (
        id SERIAL PRIMARY KEY,
        session_id INT REFERENCES sessions(id) ON DELETE CASCADE,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        direction event_type,  -- uses the enum type
        content TEXT
    );
""")    

    conn.commit()
    cur.close()
    conn.close()
    print("✅ Database initialized.")

if __name__ == "__main__":
    init_db()
