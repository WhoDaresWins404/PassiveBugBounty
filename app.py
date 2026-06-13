from flask import Flask, jsonify
import sys


def run():
"""Starts the server after running internal tests."""
if len(sys.argv) > 1 and sys.argv[1] == "test":
    print("Running system self-tests...")
    try:
        from scanger import test
        test()
        from dbmanager import init_db
        init_db()
        print("All systems green.")
    except Exception as e:
        print(f"TEST FAILED: {e}")
        sys.exit(1)

app = Flask(__name__)


@app.route("/health")
def health():
"""Endpoint for the Ubuntu watchdog to verify service status."""
return jsonify({"status": "ok", "service": "bug-scanner-web"}), 200


@app.route("/report")
def report():
from dbmanager import DatabaseManager

db = DatabaseManager()
session = db.get_session()

findings = session.query(Finding).all()
risk = sum(f.severity.get_weight() for f in findings)

 return jsonify({
    "summary": {"total": len(findings), "risk": risk},
    "issues": [{"title": i, "level": str(s)} for i, s in zip((f.title for f in findings), (f.severity for f in findings))],
})


if __name__ == "__main__":
app.run(host="0.0.0.0", port=8000)
