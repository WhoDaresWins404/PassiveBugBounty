from flask import jsonify
from dataclasses import asdict
import models


def get_status():
    result = models.get_latest_results()
    if not result:
        return {"progress": 0, "message": "No recent scan found"}, 404
    return {
        "progress": result.progress_pct,
        "message": result.status_message
    }


def get_results():
    result = models.get_latest_results()
    if not result:
        return {"error": "No scan results to display"}, 404

    findings = [asdict(finding) for finding in result.findings]
    return {
        "status": result.status_message,
        "progress": result.progress_pct,
        "findings": findings
    }
