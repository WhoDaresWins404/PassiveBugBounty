import logging
from unittest.mock import MagicMock
from dbmanager import DatabaseManager, Severity


LOG = logging.getLogger(__name__)


def check_hsts(flow):
    headers = [k.lower() for k in flow.response.headers]
    if "strict-transport-security" not in headers:
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
    result = Finding(scan_id=scan_id, severity=severity, title=title, description=description)
    session.add(result)
    session.commit()


def proxy_handler(flow):
    check_hsts(flow)
    check_headers(flow)
    check_body(flow)

def options(options):
    return None

# SELF TEST SUITE FOR SCAN ENGINE
def test():
    mock_flow = MagicMock()
    mock_session = MagicMock()
    dbmanager = DatabaseManager()
    dbmanager.get_session.return_value = mock_session
    mock_flow.request = [1]

    # Test HSTS failure (empty headers)
    mock_flow.response.headers = []
    check_hsts(mock_flow)
    assert session.add.called

    # Test Missing Headers
    mock_flow.response.headers = ["Content-Type"]
    check_headers(mock_flow)
    assert mock_session.commit.called

    # Test Plaintext Credential (simulated via a fake response body string)
    mock_flow.response.text = "password=123456"
    check_body(mock_flow)
    assert mock_session.add.called
