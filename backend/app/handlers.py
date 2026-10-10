import os
import copy
import io
import csv
import time
import secrets
import hashlib
import random
import logging
import jwt
import json
from datetime import datetime, timezone
from typing import List
from fastapi import FastAPI, HTTPException, Request, WebSocket, WebSocketDisconnect
from fastapi.responses import StreamingResponse
from openpyxl import Workbook
from contextlib import asynccontextmanager
from app.seed_data import (
    DISC_INTERPRETATIONS,
    SCENARIO_ASSESSMENT_VERSION,
    SCENARIO_ITEMS,
)
DB_DSN = os.environ.get("DB_DSN", "postgresql://axelbit:ax3lb1t@localhost/internxam_db")
from app.core.config import JWT_SECRET, JWT_ALGO, TOKEN_CHARSET
from app.core.security import (
    create_access_token as create_signed_access_token,
)
from app.db.lifecycle import close_database, open_database
from app.services.scenario_assessment import compute_scenario_result

DB_DSN = os.environ.get("DB_DSN", "******localhost/internxam_db")

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
async def lifespan(app: FastAPI):
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

DEFAULT_CONFIG = {"id": "main", "tkj_duration_minutes": 60, "disc_duration_minutes": 20, "tkj_question_count": 25, "violation_threshold": 3, "require_seb": False, "seb_browser_exam_key": ""}

async def get_config() -> dict:
    async with pool.acquire() as conn:
        cfg = await conn.fetchrow("SELECT * FROM exam_configs WHERE id = 'main'")
        if not cfg:
            await conn.execute("INSERT INTO exam_configs (id, tkj_duration_minutes, disc_duration_minutes, tkj_question_count, violation_threshold, require_seb, seb_browser_exam_key) VALUES ($1, $2, $3, $4, $5, $6, $7)",
                               "main", 60, 20, 25, 3, False, "")
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

async def get_session(participant_id: str, token_code: str) -> tuple:
    async with pool.acquire() as conn:
        p = await conn.fetchrow("SELECT * FROM participants WHERE id = $1", participant_id)
        if not p or p["token_code"] != token_code.upper(): raise HTTPException(404, "Sesi tidak ditemukan")
        t = await conn.fetchrow("SELECT * FROM tokens WHERE code = $1", token_code.upper())
        if not t: raise HTTPException(404, "Token tidak ditemukan")
        if t["status"] in ("completed", "expired", "revoked"): raise HTTPException(403, "Token sudah tidak berlaku")
        return dict(p), dict(t)

def remaining_seconds(started_at, duration_minutes: int) -> int:
    if not started_at: return 0
    elapsed = (now_utc() - parse_dt(started_at)).total_seconds()
    return max(0, int(duration_minutes * 60 - elapsed))

async def tkj_questions_for(p: dict) -> list:
    async with pool.acquire() as conn:
        order = json.loads(p.get("question_order") or "[]")
        qids = [o["qid"] for o in order]
        if not qids: return []
        qdocs = await conn.fetch("SELECT id, text, category, options FROM questions WHERE id = ANY($1::varchar[])", qids)
        qmap = {q["id"]: dict(q, options=json.loads(q['options'])) for q in qdocs}
        out = []
        for o in order:
            q = qmap.get(o["qid"])
            if q: out.append({"id": q["id"], "text": q["text"], "category": q.get("category", ""), "options": [q["options"][i] for i in o["option_order"]]})
        return out

def display_answers(p: dict) -> dict:
    order = json.loads(p.get("question_order") or "[]")
    omap = {o["qid"]: o["option_order"] for o in order}
    out = {}
    answers = json.loads(p.get("tkj_answers") or "{}")
    for qid, orig in answers.items():
        o = omap.get(qid)
        if o is not None and orig in o: out[qid] = o.index(orig)
    return out

async def score_tkj(p: dict) -> int:
    async with pool.acquire() as conn:
        order = json.loads(p.get("question_order") or "[]")
        qids = [o["qid"] for o in order]
        if not qids: return 0
        qdocs = await conn.fetch("SELECT id, correct_index FROM questions WHERE id = ANY($1::varchar[])", qids)
        correct = {q["id"]: q["correct_index"] for q in qdocs}
        answers = json.loads(p.get("tkj_answers") or "{}")
        return sum(1 for qid, ans in answers.items() if correct.get(qid) == ans)

async def do_submit_tkj(p: dict, auto: bool = False) -> dict:
    score = await score_tkj(p)
    order = json.loads(p.get("question_order") or "[]")
    scenario_started_at = now_utc()
    scenario_snapshot = copy.deepcopy(SCENARIO_ITEMS)
    random.shuffle(scenario_snapshot)
    for item in scenario_snapshot:
        random.shuffle(item["options"])
    update = {
        "tkj_score": score,
        "tkj_total": len(order),
        "tkj_submitted_at": scenario_started_at,
        "stage": "scenario",
        "scenario_started_at": scenario_started_at,
        "scenario_items_snapshot": json.dumps(scenario_snapshot),
        "scenario_version": SCENARIO_ASSESSMENT_VERSION,
        "auto_submitted": bool(p.get("auto_submitted")) or auto,
    }
    async with pool.acquire() as conn:
        await conn.execute(
            """UPDATE participants
               SET tkj_score=$1, tkj_total=$2, tkj_submitted_at=$3, stage=$4,
                   scenario_started_at=$5, scenario_items_snapshot=$6, scenario_version=$7,
                   auto_submitted=$8
               WHERE id=$9""",
            update["tkj_score"], update["tkj_total"], update["tkj_submitted_at"], update["stage"],
            update["scenario_started_at"], update["scenario_items_snapshot"],
            update["scenario_version"], update["auto_submitted"], p["id"],
        )
    return update

async def compute_scenario(p: dict) -> dict:
    items = p.get("scenario_items_snapshot") or json.dumps(SCENARIO_ITEMS)
    answers = p.get("scenario_answers") or "{}"
    if isinstance(items, str):
        items = json.loads(items)
    if isinstance(answers, str):
        answers = json.loads(answers)
    return compute_scenario_result(items, answers, p.get("scenario_version") or SCENARIO_ASSESSMENT_VERSION)

async def compute_disc(p: dict) -> dict:
    async with pool.acquire() as conn:
        items = await conn.fetch("SELECT * FROM disc_items ORDER BY group_index ASC")
    most, least = {"D": 0, "I": 0, "S": 0, "C": 0}, {"D": 0, "I": 0, "S": 0, "C": 0}
    answers = json.loads(p.get("disc_answers") or "{}")
    for item in items:
        stmts = json.loads(item["statements"])
        ans = answers.get(str(item["group_index"]))
        if not ans: continue
        if 0 <= ans["most"] < len(stmts): most[stmts[ans["most"]]["dimension"]] += 1
        if 0 <= ans["least"] < len(stmts): least[stmts[ans["least"]]["dimension"]] += 1
    change = {d: most[d] - least[d] for d in "DISC"}
    dominant = max(change, key=lambda d: change[d])
    return {"most": most, "least": least, "change": change, "dominant": dominant, "interpretation": DISC_INTERPRETATIONS.get(dominant, ""), "answered_groups": len(answers), "total_groups": len(items)}

async def do_complete(p: dict, auto: bool = False) -> dict:
    result = await compute_scenario(p) if p.get("stage") == "scenario" else await compute_disc(p)
    result_column = "scenario_result" if p.get("stage") == "scenario" else "disc_result"
    update = {
        result_column: json.dumps(result),
        "stage": "done",
        "completed_at": now_utc(),
        "auto_submitted": bool(p.get("auto_submitted")) or auto,
    }
    async with pool.acquire() as conn:
        await conn.execute(
            f"UPDATE participants SET {result_column}=$1, stage=$2, completed_at=$3, auto_submitted=$4 WHERE id=$5",
            update[result_column], update["stage"], update["completed_at"], update["auto_submitted"], p["id"],
        )
        # Only mark token complete if single, group tokens stay active until all users complete? Let's just leave group tokens active.
        t = await conn.fetchrow("SELECT type FROM tokens WHERE code=$1", p["token_code"])
        if t and t["type"] != "group":
            await conn.execute("UPDATE tokens SET status='completed', completed_at=$1 WHERE code=$2", update["completed_at"], p["token_code"])
    completion_label = "asesmen skenario PKL" if result_column == "scenario_result" else "Psikotes DISC"
    await manager.broadcast({"type": "exam_complete", "participant": p["name"], "detail": f"menyelesaikan {completion_label}"})
    return update

async def build_state(p: dict, t: dict, cfg: dict) -> dict:
    async with pool.acquire() as conn:
        p = dict(await conn.fetchrow("SELECT * FROM participants WHERE id = $1", p["id"]))
        vcount = await conn.fetchval("SELECT COUNT(*) FROM violation_logs WHERE participant_id = $1", p["id"])
    state = {"participant_id": p["id"], "name": p["name"], "stage": p["stage"], "violation_count": vcount, "violation_threshold": cfg["violation_threshold"]}
    if p["stage"] == "tkj":
        rem = remaining_seconds(p["tkj_started_at"], cfg["tkj_duration_minutes"])
        if rem <= 0:
            await do_submit_tkj(p, auto=False)
            return await build_state(p, t, cfg)
        state.update({"questions": await tkj_questions_for(p), "answers": display_answers(p), "remaining_seconds": rem})
    elif p["stage"] == "disc":
        rem = remaining_seconds(p["disc_started_at"], cfg["disc_duration_minutes"])
        if rem <= 0:
            await do_complete(p, auto=False)
            return await build_state(p, t, cfg)
        async with pool.acquire() as conn:
            items = await conn.fetch("SELECT * FROM disc_items ORDER BY group_index ASC")
        state.update({"disc_items": [{"group_index": i["group_index"], "statements": [s["text"] for s in json.loads(i["statements"])]} for i in items],
                      "disc_answers": json.loads(p.get("disc_answers") or "{}"), "remaining_seconds": rem})
    elif p["stage"] == "scenario":
        rem = remaining_seconds(p["scenario_started_at"], cfg["disc_duration_minutes"])
        if rem <= 0:
            await do_complete(p, auto=False)
            return await build_state(p, t, cfg)
        items = p.get("scenario_items_snapshot") or json.dumps(SCENARIO_ITEMS)
        answers = p.get("scenario_answers") or "{}"
        if isinstance(items, str):
            items = json.loads(items)
        if isinstance(answers, str):
            answers = json.loads(answers)
        state.update({
            "scenario_version": p.get("scenario_version") or SCENARIO_ASSESSMENT_VERSION,
            "scenario_items": [
                {"id": item["id"], "situation": item["situation"], "options": [option["text"] for option in item["options"]]}
                for item in items
            ],
            "scenario_answers": answers,
            "remaining_seconds": rem,
        })
    return state

async def websocket_live(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True: await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)
