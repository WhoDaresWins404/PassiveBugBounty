from abc import ABC, abstractmethod
from typing import List


class BaseAnalyzer(ABC):
    """Base class for all vulnerability detection modules."""
    @abstractmethod
    def analyze(self, request_json: dict) -> list[dict]:
        pass

class TrafficIngestor:
    def __init__(self, analyzers: List[BaseAnalyzer]):
        self.analyzers = analyzers

    def process_capture(self, session_id, method, url, request_body, response_json):
        # This would call add_capture from src/models in the real app
        from .models import add_capture
        session = add_capture(None, session_id, method, url, request_body, response_json)

        if not session:
            return []

        results = []
        for analyzer in self.analyzers:
            findings = analyzer.analyze({"method": method, "url": url, "body": request_body})
            results.extend(findings)
        return results
