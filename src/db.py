import sqlite3
import json


def init_db():
    conn = sqlite3.connect("traffic_analyzer.db")
    cursor = conn.cursor()
    # Unstructured pool
    cursor.execute(
        "CREATE TABLE IF NOT EXISTS all_scans (id INTEGER PRIMARY KEY, raw_json TEXT)"
    )
    # Structured pools by classification
    tables = ["ssrf", "sqli", "xss", "path_traversal", "cmdi"]
    for table in tables:
        cursor.execute(
            f"CREATE TABLE IF NOT EXISTS {table} (id INTEGER PRIMARY KEY, type TEXT, severity TEXT, confidence REAL)"
        )
    conn.commit()
    conn.close()


def save_finding(vuln_type, severity, confidence, description, raw_data):
    conn = sqlite3.connect("traffic_analyzer.db")
    cursor = conn.cursor()

    # Save to unstructured pool
    raw_json = json.dumps(raw_data)
    cursor.execute("INSERT INTO all_scans (raw_json) VALUES (?)", (raw_json,))

    # Route to specific classification table
    table_map = {
        "SQLi": "sqli",
        "XSS": "xss",
        "SSRF": "ssrf",
        "Path Traversal": "path_traversal",
        "CMDi": "cmdi",
    }

    if vuln_type in table_map:
        table = table_map[vuln_type]
        cursor.execute(
            f"INSERT INTO {table} (type, severity, confidence) VALUES (?, ?, ?)",
            (vuln_type, severity, confidence),
        )

    conn.commit()
    conn.close()
