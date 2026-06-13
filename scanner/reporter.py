from database import Finding


def report_findings(findings):
    results = []
    for title, severity in findings:
        finding = Finding(title=title, severity=severity)
        dbmanager.session().add(finding)
    dbmanager.session().commit()
    return results

