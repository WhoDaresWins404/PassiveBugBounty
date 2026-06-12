# src/correlator/session_builder.py
import asyncio
import json
import asyncpg
import redis.asyncio as redis
from src.config import settings
from src.storage.jsonl_pool import UnstructuredPool

class SessionCorrelator:
    def __init__(self):
        self.redis: redis.Redis = None
        self.postgres: asyncpg.Pool = None
        self.pool = UnstructuredPool()
        self.queue_name = "traffic_ingress_queue"
        self.state_prefix = "session_state:"

    async def start(self):
        """Initialize connections and start the processing loop."""
        print("🔄 Starting Session Correlator...")
        
        # 1. Connect to Redis
        self.redis = redis.from_url(settings.redis_url, decode_responses=True)
        
        # 2. Connect to PostgreSQL Pool
        self.postgres = await asyncpg.create_pool(settings.postgres_url)
        
        print("✅ Session Correlator connected to Redis and PostgreSQL.")
        
        # 3. Start background TTL cleanup task
        asyncio.create_task(self._ttl_cleanup_loop())
        
        # 4. Start main processing loop
        await self._process_queue()

    async def _process_queue(self):
        """Continuously listen to the Redis queue for traffic metadata."""
        while True:
            try:
                # BRPOP blocks until an item is available (efficient, no polling)
                result = await self.redis.brpop(self.queue_name, timeout=5)
                if result:
                    _, payload_str = result
                    payload = json.loads(payload_str)
                    await self._handle_event(payload)
            except asyncio.CancelledError:
                break
            except Exception as e:
                print(f"❌ Error in correlator loop: {e}")
                await asyncio.sleep(1) # Backoff on error

    async def _handle_event(self, payload: dict):
        """Merge request and response events using Redis Hashes."""
        corr_id = payload.get("correlation_id")
        direction = payload.get("direction")
        
        if not corr_id or not direction:
            return

        state_key = f"{self.state_prefix}{corr_id}"
        
        if direction == "request":
            # Store request data in Redis Hash
            await self.redis.hset(state_key, mapping={"request": json.dumps(payload)})
        elif direction == "response":
            # Store response data and check if request exists
            await self.redis.hset(state_key, mapping={"response": json.dumps(payload)})
            
            # Check if we have both parts
            session_data = await self.redis.hgetall(state_key)
            if "request" in session_data and "response" in session_data:
                await self._finalize_session(corr_id, session_data)
                # Clean up state
                await self.redis.delete(state_key)

    async def _finalize_session(self, corr_id: str, state: dict):
        """Merge, save to Postgres, and append to JSONL pool."""
        req_data = json.loads(state["request"])
        res_data = json.loads(state["response"])
        
        # Merge into a single structured record
        merged_session = {
            "correlation_id": corr_id,
            "timestamp": req_data.get("timestamp"),
            "host": req_data.get("host"),
            "method": req_data.get("method"),
            "path": req_data.get("path"),
            "request_headers": req_data.get("request_headers"),
            "response_status": res_data.get("response_status"),
            "response_headers": res_data.get("response_headers"),
            "request_content_length": req_data.get("request_content_length", 0),
            "response_content_length": res_data.get("response_content_length", 0),
            "is_suspicious": req_data.get("is_suspicious", False)
        }

        # 1. Save to PostgreSQL
        await self._save_to_postgres(merged_session)
        
        # 2. Append to Unstructured JSONL Pool
        await self.pool.append_session(merged_session)
        
        print(f"💾 Correlated & Saved Session: {corr_id} | {merged_session['method']} {merged_session['host']} -> {merged_session['response_status']}")

    async def _save_to_postgres(self, session: dict):
        """Insert the merged session into the minimal safe storage schema."""
        async with self.postgres.acquire() as conn:
            await conn.execute("""
                INSERT INTO http_sessions (
                    correlation_id, timestamp, host, method, path, 
                    request_headers, response_status, response_headers,
                    request_content_length, response_content_length, is_suspicious
                ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11)
                ON CONFLICT (correlation_id) DO NOTHING
            """, 
                session["correlation_id"],
                session["timestamp"],
                session["host"],
                session["method"],
                session["path"],
                json.dumps(session["request_headers"]),
                session["response_status"],
                json.dumps(session["response_headers"]),
                session["request_content_length"],
                session["response_content_length"],
                session["is_suspicious"]
            )

    async def _ttl_cleanup_loop(self):
        """Run the TTL cleanup every 6 hours."""
        while True:
            await asyncio.sleep(6 * 3600) # 6 hours
            try:
                await self.pool.enforce_ttl()
            except Exception as e:
                print(f"⚠️ TTL Cleanup failed: {e}")