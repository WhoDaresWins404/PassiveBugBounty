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
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            client_ip INET,
            start_time TIMESTAMPTZ DEFAULT NOW()
        );
        
        CREATE TYPE IF NOT EXISTS event_type AS ENUM ('request', 'response');
        
        CREATE TABLE IF NOT EXISTS http_events (
            id BIGSERIAL PRIMARY KEY,
            session_id UUID REFERENCES sessions(id),
            type event_type NOT NULL,
            path TEXT,
            method TEXT,
            status_code INT,
            headers JSONB
        );
    """)
    
    conn.commit()
    cur.close()
    conn.close()
    print("✅ Database initialized.")

if __name__ == "__main__":
    init_db()
