# ./app/utils/__init__.py
from django_utils import dedup  # Placeholder for deduplication logic if needed by extra layers


def get_session_summary(session_id):
    """Aggregation helper for the Dashboard view."""
    with SessionLocal() as db:
        return db.query(TrafficEntry).filter(
            TrafficEntry.session_id == session_id
        ).all()