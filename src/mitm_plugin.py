from mitmproxy import http
from .storage import save_endpoint

def endpoint_analyzer(flow):
    # Placeholder logic: in production, regex/signature matching goes here
    category = None
    if "select" in flow.request.path and "1=1" in flow.request.query:
        category = "sqli"
    elif "/etc/passwd" in flow.request.path:
        category = "path_traversal"

    save_endpoint(flow.request.url, flow.request.method, category)
