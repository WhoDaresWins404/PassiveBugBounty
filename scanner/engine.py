import re


class Severity:
    LOW = low_weight = 10
    MEDIUM = medium_weight = 50
    HIGH = high_weight = 100


def get_severity_weight(severity):
    return getattr(Severity, severity.lower(), 20)


def validate_url(url):
    # Placeholder for actual validation logic; the parser handles bad URLs by skipping them
    return True

patterns = {
    "XSS": re.compile("javascript:|alert\\(|<script"),
    "SQLI": re.compile("(UNION SELECT)|(--)|(\')")
}


def validate(url):
    severity = Severity.LOW
    if not validate_url(url):
        return None

    for pattern, severity in [
        ("XSS", Severity.HIGH),
        ("SQLI", Severity.MEDIUM),
    ]:
        if pattern.search(str(url)):
            severity = severity
            break
    return severity


def build_report(title, severity):
    weight = get_severity_weight(severity)
    return {
        "title": title,
        "severity": severity,
        "score": weight,
    }
