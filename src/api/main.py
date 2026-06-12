# src/api/main.py
from fastapi import FastAPI
from pydantic import BaseModel
from typing import List
import asyncpg
from src.config import settings


app = FastAPI(title="Passive Analyzer API", version="0.1.0")

# Simple health check endpoint (from Architecture Doc)
@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "analyzer-api"}

# Placeholder endpoint for future P2 Detection
@app.post("/detect")
async def detect_payload(payload: dict):
    return {"status": "queued_for_analysis"}

# Endpoint to fetch recent metadata from PostgreSQL (P0 Goal)
@app.get("/api/sessions/recent")
async def get_recent_sessions(limit: int = 10):
    # This will eventually query your PostgreSQL metadata table
    # For now, returning mock data to prove the API works
    return {
        "sessions": [
            {"correlation_id": "abc-123", "host": "example.com", "method": "GET", "status": 200},
            {"correlation_id": "def-456", "host": "test.local", "method": "POST", "status": 401}
        ]
    }

@app.get("/api/sessions/recent")
async def get_recent_sessions(limit: int = 20):
    try:
        conn = await asyncpg.connect(settings.postgres_url)
        try:
            records = await conn.fetch("""
                SELECT correlation_id, timestamp, host, method, path, response_status, is_suspicious
                FROM http_sessions
                ORDER BY timestamp DESC
                LIMIT $1
            """, limit)
            
            # Convert asyncpg Records to dicts
            sessions = [dict(r) for r in records]
            return {"sessions": sessions}
        finally:
            await conn.close()
    except Exception as e:
        return {"error": str(e), "sessions": []}