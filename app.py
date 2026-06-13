from Flask import Flask, jsonify
from dbmanager import DatabaseManager

app = Flask(__name__)


@app.route('/status')
def get_report():
    dbmanager = DatabaseManager()
    session = dbmanager.get_session()

    findings = session.query(Finding).all()
    weighted_score = sum(f.severity.get_weight() for f in findings)

    return jsonify({
        "total_issues": len(findings),
        "risk_index": weighted_score,
        "details": [{"id": i, "title": t} for i,t in [(f.id, f.title) for f in findings]]
    })


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
