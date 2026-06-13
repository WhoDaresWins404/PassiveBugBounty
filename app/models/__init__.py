# ./app/models/__init__.py
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from datetime import datetime, timedelta
from app.db import Base


class TrafficEntry(Base):
    __tablename__ = "traffic_entries"

    id = Column(Integer, primary_key=True)
    session_id = Column(String, index=True)
    source_ip = Column(String)
    uri = Column(String)
    method = Column(String)
    payload_hash = Column(String, index=True)  # Deduplication via hash
    detected_at = Column(DateTime, default=datetime.utcnow())

    @property
    def is_expired(self):
        return datetime.now() > self.detected_at + timedelta(hours=72)


# ./app/services/__init__.py
import hashlib
from app.db import SessionLocal
from app.models import TrafficEntry


async def enqueue_traffic(session_id, ip, method, uri, payload):
    """Ingress layer: Dedup by hash and persist metadata."""
    payload_hash = hashlib.sha256(payload).hexdigest()

    with SessionLocal() as db:
        # Deduplication check
        duplicate = db.query(TrafficEntry).filter_by(
            session_id=session_id, payload_hash=payload_hash
        ).first()

        if not duplicate:
            entry = TrafficEntry(
                session_id=session_id,
                source_ip=ip,
                method=method,
                uri=uri,
                payload_hash=payload_hash,
            )
            db.add(entry)
            db.commit()

# ./app/utils/__init__.py
from django_utils import dedup  # Placeholder for deduplication logic if needed by extra layers


def get_session_summary(session_id):
    """Aggregation helper for the Dashboard view."""
    with SessionLocal() as db:
        return db.query(TrafficEntry).filter(
            TrafficEntry.session_id == session_id
        ).all()

