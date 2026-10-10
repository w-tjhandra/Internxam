import os
import io
import csv
import time
import secrets
import hashlib
import logging
import jwt
from datetime import datetime, timezone
from typing import List
from fastapi import FastAPI, HTTPException, Request, WebSocket, WebSocketDisconnect
from fastapi.responses import StreamingResponse
from openpyxl import Workbook
from contextlib import asynccontextmanager
from app.core.config import JWT_SECRET, JWT_ALGO, TOKEN_CHARSET
DB_DSN = os.environ.get("DB_DSN", "postgresql://axelbit:ax3lb1t@localhost/internxam_db")
from app.core.security import (
    create_access_token as create_signed_access_token,
)
from app.db.lifecycle import close_database, open_database

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception:
                pass

manager = ConnectionManager()
pool = None

@asynccontextmanager
async def lifespan(_app: FastAPI):
    global pool
    pool = await open_database(DB_DSN)
    try:
        yield
    finally:
        await close_database(pool)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("securecbt")

def now_utc(): return datetime.now(timezone.utc)
def iso(dt): return dt.isoformat() if dt else None
def parse_dt(s): return s if isinstance(s, datetime) and s.tzinfo else datetime.fromisoformat(s) if isinstance(s, str) else s.replace(tzinfo=timezone.utc) if isinstance(s, datetime) else None

def create_access_token(admin_id: str, email: str) -> str:
    return create_signed_access_token(admin_id, email, JWT_SECRET, JWT_ALGO)

async def get_current_admin(request: Request) -> dict:
    token = request.cookies.get("access_token") or (request.headers.get("Authorization", "")[7:] if request.headers.get("Authorization", "").startswith("Bearer ") else None)
    if not token: raise HTTPException(401, "Not authenticated")
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGO])
        if payload.get("type") != "access": raise HTTPException(401, "Invalid token type")
        async with pool.acquire() as conn:
            admin = await conn.fetchrow("SELECT id, email, name, role FROM admins WHERE id = $1", payload["sub"])
            if not admin: raise HTTPException(401, "Admin not found")
            return dict(admin)
    except Exception: raise HTTPException(401, "Invalid or expired token")

DEFAULT_CONFIG = {"id": "main", "tkj_duration_minutes": 60, "disc_duration_minutes": 20, "tkj_question_count": 25, "violation_threshold": 3, "require_seb": False, "seb_browser_exam_key": "", "work_disc_enabled": True, "work_disc_duration_minutes": 60}

async def get_config() -> dict:
    async with pool.acquire() as conn:
        cfg = await conn.fetchrow("SELECT * FROM exam_configs WHERE id = 'main'")
        if not cfg:
            await conn.execute("INSERT INTO exam_configs (id, tkj_duration_minutes, disc_duration_minutes, tkj_question_count, violation_threshold, require_seb, seb_browser_exam_key, work_disc_enabled, work_disc_duration_minutes) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)",
                               "main", 60, 20, 25, 3, False, "", True, 60)
            return dict(DEFAULT_CONFIG)
        return dict(cfg)

async def verify_seb(request: Request):
    cfg = await get_config()
    if not cfg.get("require_seb"): return
    bek = cfg.get("seb_browser_exam_key", "")
    req_hash, cfg_hash = request.headers.get("X-SafeExamBrowser-RequestHash", ""), request.headers.get("X-SafeExamBrowser-ConfigKeyHash", "")
    if not req_hash and not cfg_hash: raise HTTPException(403, "Ujian ini wajib menggunakan Safe Exam Browser (SEB)")
    if bek and req_hash:
        url = str(request.url).replace("http://", "https://", 1) if request.url.scheme == "http" else str(request.url)
        if req_hash.lower() not in (hashlib.sha256((url + bek).encode()).hexdigest(), hashlib.sha256((str(request.url) + bek).encode()).hexdigest()):
            raise HTTPException(403, "Verifikasi Browser Exam Key gagal")

_rate: dict = {}
def rate_limit(ip: str, key: str, limit: int = 10, window: int = 60):
    global _rate
    if len(_rate) > 2000: _rate = {}
    bucket = f"{ip}:{key}"
    nowt = time.time()
    hits = [t for t in _rate.get(bucket, []) if nowt - t < window]
    if len(hits) >= limit: raise HTTPException(429, "Terlalu banyak percobaan")
    hits.append(nowt)
    _rate[bucket] = hits

def gen_token_code() -> str: return "".join(secrets.choice(TOKEN_CHARSET) for _ in range(8))

def build_export(headers, rows, name, fmt):
    if fmt == "xlsx":
        wb = Workbook(); ws = wb.active
        ws.append(headers)
        for r in rows: ws.append(r)
        buf = io.BytesIO(); wb.save(buf); buf.seek(0)
        return StreamingResponse(buf, media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", headers={"Content-Disposition": f"attachment; filename={name}.xlsx"})
    buf = io.StringIO(); w = csv.writer(buf)
    w.writerow(headers); w.writerows(rows)
    return StreamingResponse(iter([buf.getvalue()]), media_type="text/csv", headers={"Content-Disposition": f"attachment; filename={name}.csv"})

async def websocket_live(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True: await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)
