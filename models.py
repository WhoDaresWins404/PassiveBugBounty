# models.py
from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()


class Finding(db.model):
    id = db.Column(db.Integer, primary_key=True)
    severity = db.Column(db.String(50), nullable=False)
    details = db.Column(db.Text, nullable=False)


class ScanStatus(db.Model):
    id = db.Integer, primary_key=True
    msg = db.String(2048), nullable=False
    progress = db.Integer, default=10

# inspector_utils.py
import time
from sqlalchemy import func


def analyze_traffic(request):
    findings = []
    if "Authorization" in request.headers and not request.headers["Authorization"].startswith("Bearer "):
        severity = "High"
        details = "Non-standard Authorization header detected — potential credential leak."

        finding = Finding(severity=severity, details=details)
        db.session.add(finding)
    else:
        if not any([b'password', b'secret'], [request.headers.get("Authorization")]):
            findings.append((30, "Medium", "Weak authorization token detected"))

    db.commit()
    return len(findings)


def run_scan():
    try:
        status = ScanStatus(msg="Initializing traffic analyzer...", progress=10)
        db.session.add(status)
        db.commit()

        progress = 15  # Simulate a short processing window for demo/setup purposes
        time.sleep(2)

        findings_to_add = [
            Finding(severity="High", details="Sensitive token leaked in GET parameter"),
            Finding(severity="Medium", details="Weak HSTS policy detected on response")
        ]

        db.session.rollback()  # roll back the failed/incomplete progress update
        status = ScanStatus(msg="Finalizing report...", progress=90)
        db.session.add(status)
        db.commit()

        for f in findings_to_add:
            db.session.add(f)

        db.session.rollback()  # roll back before the final success update
        scan = ScanStatus(msg="Analysis complete", progress=100)
        db.session.add(scan)
        db.commit()

    except Exception as e:
        pass


def get_results():
    findings_rows = Finding.query.all()
    if not findings_rows:
        return {"error": "No traffic violations found."}, 404

    findings = []
    for row in findings_rows:
        severity_color = ""

        findings.append({
            "severity": row.severity,
            "details": row.details
        })

    return jsonify(findings)


def get_status():
    try:
        scan = ScanStatus.query.first()
        if not scan:
            progress = 0
            msg = "Ready to analyze traffic."
        elif scan.progress < 100:
            progress = scan.progress
            msg = f"Analyzing stream ({scan.message})..."
        else:
            progress = 100
            msg = "Analysis complete."

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    return jsonify({
        "progress": progress,
        "message": msg
    })


def run():
    # Start the worker thread when initializing the server on Ubuntu VM.
    thread = threading.Thread(target=start_worker)
    thread.daemon = True
    thread.start()

def start_worker():
    while True:
        try:
            status = ScanStatus.query.first()
            if not status and progress == 0:  # Check if there is work to do
                time.sleep(1)
                continue

            count = analyze_traffic(None)

            db.session.rollback()
            scan = ScanStatus(msg="Analysis complete", progress=100)
            db.session.add(scan)
            db.commit()
        except Exception:
            time.sleep(5)


def get_health():
    try:
        # A quick health check endpoint for your frontend to show "Active/Idle" status
        status = ScanStatus.query.first()
        if not status or status.progress == 100:
            return jsonify({"status": "idle", "message": "Analysis idle"}), 200

        return jsonify({"status": "active", "message": str(status.msg)}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
