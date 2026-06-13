import logging
from dbmanager import DatabaseManager, Severity


LOG = logging.getLogger(__name__)


def check_hsts(flow):
    if "Strict-Transport-Security" not in [k.lower() for k in flow.response.headers]:
        severity = Severity.HIGH
        dbmanager = DatabaseManager()
        session = dbmanager.get_session()
        save_finding(session, flow.request[1], severity, "Missing HSTS", "")


def check_headers(flow):
    needed = ["X-Frame-Options", "X-Content-Type-Options", "CSP"]
    response_keys = [k.lower() for k in flow.response.headers]

    for header in needed:
        if not any(key == header for key in response_keys):
            severity = Severity.MEDIUM
            dbmanager = DatabaseManager()
            session = dbmanager.get_session()
            save_finding(session, flow.request[1], severity, f"Missing {header}", "")


def check_body(flow):
    if "password=" in str(flow.response.text).lower():
        severity = Severity.HIGH
        dbmanager = DatabaseManager()
        session = dbmanager.get_session()
        save_finding(session, flow.request[1], severity, "Plain-text credential", "")


def save_finding(session, scan_id, severity, title, description):
    from dbmanager import Finding
    finding = Finding(scan_id=scan_id, severity=severity, title=title, description=description)
    session.add(finding)
    session.commit()


def proxy_handler(flow):
    scans = [check_hsts(flow), check_headers(flow), check_body(flow)]


def options(options):
    return None
