from mitmproxy import http
from src.analyzer import scan_request


class TrafficAnalyzerProxy:
    def __init__(self):
        pass

    def response(self, flow):
        """
        Analyzes each request as it passes through the proxy.
        """
        method = flow.request.method
        url = flow.request.full_uri
        body = flow.request.content

        findings = scan_request(method, url, body)

        if findings:
            print(f"[!] Detected {len(findings)} issue(s) on {url}")
