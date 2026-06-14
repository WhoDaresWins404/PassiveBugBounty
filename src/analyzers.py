from src.models import BERTAnalyzer
from src.db import save_finding


def scan_request(method, url, body):
    """
    Analyzes a request using multiple BERT models and saves findings to the database.
    Returns a list of detected vulnerabilities.
    """
    analyzer = BERTAnalyzer()
    findings = analyzer.analyze(method, url, body)

    for finding in findings:
        save_finding(
            vuln_type=finding["type"],
            severity=finding["severity"],
            confidence=finding["confidence"],
            description=finding["description"],
            raw_data={"method": method, "url": url, "body": body},  # Unstructured pool
        )

    return findings
