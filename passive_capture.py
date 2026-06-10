from mitmproxy import http, ctx
import os
import psycopg2
import uuid
import json
from dotenv import load_dotenv

load_dotenv()

class PassiveCapture:
    def __init__(self):
        self.conn = psycopg2.connect(os.getenv("DATABASE_URL"))
        self.sessions = {}  # session_id → client_ip
    
    def _get_session(self, flow: http.HTTPFlow) -> str:
        # Create or reuse a session per unique IP + origin
        key = f"{flow.client_conn.ip_address[0]}:{flow.request.host}"
        if key not in self.sessions:
            cur = self.conn.cursor()
            cur.execute("INSERT INTO sessions (client_ip) VALUES (%s) RETURNING id", 
                        (key.split(':')[0],))
            self.sessions[key] = cur.fetchone()[0]
            self.conn.commit()
            cur.close()
        return self.sessions[key]

    def request(self, flow: http.HTTPFlow):
        session_id = self._get_session(flow)
        headers = {k: v for k, v in flow.request.headers.items() 
                   if k.lower() not in ["cookie", "authorization"]}
        
        cur = self.conn.cursor()
        cur.execute(
            """INSERT INTO http_events 
               (session_id, type, path, method, status_code, headers)
               VALUES (%s, 'request', %s, %s, NULL, %s)""",
            (session_id, flow.request.path, flow.request.method, json.dumps(headers))
        )
        self.conn.commit()
        cur.close()

    def response(self, flow: http.HTTPFlow):
        session_id = self._get_session(flow)
        headers = {k: v for k, v in flow.response.headers.items() 
                   if k.lower() not in ["set-cookie", "www-authenticate"]}
        
        cur = self.conn.cursor()
        cur.execute(
            """INSERT INTO http_events 
               (session_id, type, path, method, status_code, headers)
               VALUES (%s, 'response', %s, NULL, %s, %s)""",
            (session_id, flow.request.path, flow.response.status_code, json.dumps(headers))
        )
        self.conn.commit()
        cur.close()

    def done(self):
        self.conn.close()

addons = [PassiveCapture()]
