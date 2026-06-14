from flask import Flask, render_template_string
import sqlite3


app = Flask(__name__)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head><title>Traffic Analyzer Dashboard</title></head>
<body>
    <h1>Unstructured Scan Logs</h1>
    <table>
        <tr><th>ID</th><th>Raw JSON Data</th></tr>
        {% for scan in all_scans %}
        <tr><td>{{scan[0]}}</td><td>{{scan[1]}}</td></tr>
        {% endfor %}
    </table>

    <h2>Classified Vulnerabilities</h2>
    <table border="1">
        <thead>
            <tr><th>Type</th><th>Severity</th><th>Confidence</th></tr>
        </thead>
        <tbody>
            {% for vuln in classified_findings %}
            <tr><td>{{vuln[0]}}</td><td>{{vuln[1]}}</td><td>{{vuln[2]}}</td></tr>
            {% endfor %}
        </tbody>
    </table>
</body>
</html>
"""

@app.route("/")
def dashboard():
    conn = sqlite3.connect("traffic_analyzer.db")
    cursor = conn.cursor()

    # Fetch all scans from the unstructured pool
    all_scans = cursor.execute("SELECT id, raw_json FROM all_scans").fetchall()

    # Combine results from all classification tables
    tables = ["ssrf", "sqli", "xss", "path_traversal", "cmdi"]
    classified_findings = []
    for table in tables:
        cursor.execute(f"SELECT type, severity, confidence FROM {table}")
        classified_findings.extend(cursor.fetchall())

    conn.close()
    return render_template_string(HTML_TEMPLATE, all_scans=all_scans, classified_findings=classified_findings)
