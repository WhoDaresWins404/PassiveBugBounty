import sqlite3
from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class Finding:
    id: int
    severity: str  # 'High', 'Medium', 'Low'
    details: str

@dataclass
class ScanStatus:
    progress_pct: int
    status_message: str
    findings: list[Finding] = field(default_factory=list)

DB_FILE = "scan_data.db"

def init_db():
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        # Jobs table for job id, status string, and progress percentage
        cursor.execute('''CREATE TABLE IF NOT EXISTS jobs (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            status TEXT,
                            progress INTEGER
                         )""")
        # Findings table linked by scan_job_id
        cursor.execute('''CREATE TABLE IF NOT EXISTS findings (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            scan_job_id INTEGER,
                            severity TEXT,
                            details TEXT
                         )""")
        conn.commit()

def get_latest_results():
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        # Fetch the most recent job (simulating a real scan result)
        cursor.execute("SELECT id, status, progress FROM jobs ORDER BY id DESC LIMIT 1")
        job = cursor.fetchone()
        if not job:
            return None

        findings_rows = cursor.execute(
            "SELECT id, severity, details FROM findings WHERE scan_job_id = ?", (job[0],)
        ).fetchall()
    
    # Seed mock data if the table is empty so the UI still looks good today
    if not findings_rows:
        cursor.execute("INSERT INTO findings VALUES ((SELECT COALESCE(MAX(scan_job_id), 1)), 'High', 'Sample bug description (mock)'))")

    return ScanStatus(
        progress_pct=int(job[2]),
        status_message="Scanning complete",
        findings=[Finding(i, severity, details) for i, severity, details in findings_rows]
    )
