"""
Traffic Ingress Module (mitmproxy Addon)
"""
import sys
import os
import asyncio
import json
import uuid
from datetime import datetime, timezone
from typing import Optional

import redis.asyncio as redis
from mitmproxy import http, ctx

# --- DYNAMIC PATH RESOLUTION ---
# Get the directory of this current file (src/ingress/)
current_dir = os.path.dirname(os.path.abspath(__file__))
# Go up two levels to get the project root
project_root = os.path.abspath(os.path.join(current_dir, "../.."))

# Add project root to sys.path if it's not already there
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Now the import will work perfectly
from src.config import settings
# --------------------------------

class TrafficIngressAddon:
    def __init__(self):
        self.redis_client: Optional[redis.Redis] = None
        self.queue_name = "traffic_ingress_queue"

    def load(self, loader):
        """Called when the addon is loaded."""
        ctx.log.info(f"[Ingress] Loading addon. Strict Passive Mode: {settings.strict_passive_mode}")
        ctx.log.info(f"[Ingress] Allowed targets: {settings.allowed_targets_list}")

    async def running(self):
        """Called when the proxy is fully running. Initialize async connections here."""
        try:
            self.redis_client = redis.from_url(
                settings.redis_url,
                decode_responses=True,
                health_check_interval=30
            )
            # Test connection
            await self.redis_client.ping()
            ctx.log.info("[Ingress] Successfully connected to Redis queue.")
        except Exception as e:
            ctx.log.error(f"[Ingress] Failed to connect to Redis: {e}")
            # In a strict production environment, you might want to raise this 
            # to prevent the proxy from running without its sink.

    async def done(self):
        """Called when the proxy shuts down."""
        if self.redis_client:
            await self.redis_client.close()
            ctx.log.info("[Ingress] Redis connection closed.")

    def _is_target_allowed(self, flow: http.HTTPFlow) -> bool:
        """Check if the requested host is in the pre-approved list."""
        host = flow.request.host
        return any(allowed in host for allowed in settings.allowed_targets_list)

    def _extract_metadata(self, flow: http.HTTPFlow) -> dict:
        """
        Extract HTTP-level metadata ONLY. 
        P0 Constraint: No body unless flagged suspicious.
        """
        correlation_id = flow.id or str(uuid.uuid4())
        
        # Basic Request Metadata
        metadata = {
            "correlation_id": correlationID,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "direction": "request",
            "method": flow.request.method,
            "url": flow.request.pretty_url,
            "host": flow.request.host,
            "path": flow.request.path,
            "request_headers": dict(flow.request.headers),
            "request_content_length": len(flow.request.content) if flow.request.content else 0,
            
            # Response Metadata (populated in response hook, but initialized here)
            "response_status": None,
            "response_headers": None,
            "response_content_length": 0,
            
            # P0 Constraints Enforcement
            "body_included": False, 
            "request_body": None,
            "response_body": None,
            "is_suspicious": False, # Placeholder for P1/P2 rule engine
            "truncated": False
        }

        # P0 Constraint: Data Minimization. 
        # If future logic flags this as suspicious, you would set body_included=True 
        # and capture flow.request.content / flow.response.content here.
        # For now, we strictly log metadata.

        return metadata

    async def request(self, flow: http.HTTPFlow):
        """Intercepts the request. We let it pass through, but log metadata."""
        if not self._is_target_allowed(flow):
            # Silently ignore or log as dropped to prevent noise
            return

        metadata = self._extract_metadata(flow)
        
        # We store the initial request metadata in the flow's custom state 
        # so we can merge it with the response later in the Session Correlator,
        # OR we push it now and let the correlator merge it via correlation_id.
        # Pushing now is better for the "Unstructured Traffic Pool" ingestor.
        await self._push_to_redis(metadata)

    async def response(self, flow: http.HTTPFlow):
        """Intercepts the response. We append response metadata and push an update."""
        if not self._is_target_allowed(flow):
            return

        # Create a response-only metadata packet, linked by correlation_id
        metadata = {
            "correlation_id": flow.id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "direction": "response",
            "response_status": flow.response.status_code,
            "response_headers": dict(flow.response.headers),
            "response_content_length": len(flow.response.content) if flow.response.content else 0,
            "response_body": None, # P0 Constraint: Metadata only
            "body_included": False,
            "is_suspicious": False
        }

        await self._push_to_redis(metadata)

    async def _push_to_redis(self, payload: dict):
        """Asynchronously push the metadata payload to the Redis queue."""
        if not self.redis_client:
            ctx.log.warn("[Ingress] Redis client not initialized. Dropping payload.")
            return

        try:
            # Push to a Redis List (acting as a simple queue)
            # In P0, we use LPUSH. The Session Correlator will use BRPOP to consume.
            await self.redis_client.lpush(self.queue_name, json.dumps(payload))
            ctx.log.debug(f"[Ingress] Pushed metadata for correlation_id: {payload.get('correlation_id')}")
        except Exception as e:
            ctx.log.error(f"[Ingress] Failed to push to Redis: {e}")

# Instantiate the addon so mitmproxy can register it
addons = [
    TrafficIngressAddon()
]