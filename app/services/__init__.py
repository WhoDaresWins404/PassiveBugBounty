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