from flask import Flask, jsonify, render_template, redirect, url_for  # Added redirect/url_for
from database import dbmanager


app = Flask(__name__)


@app.route("/")
def index():
    return redirect(url_for("dashboard"))


@app.route("/status/<job_id>", methods=["GET"])
def get_scan_status(job_id):
    # Mock status for now - replace with real job lookup in the worker queue
    return jsonify({"status": "processing", "progress": 45})


@app.route("/report/<int:finding_id>")
def get_finding(finding_id):
    result = {"title": f"Finding #{finding_id}", "severity": "high", "details": "Sample bug description"}
    return jsonify(result)


@app.route("/dashboard")
def dashboard():
    # This is what resolves your 404 — the landing page for the end user
    return render_template("index.html")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)  # Added this so python execution starts the server
