from dotenv import load_dotenv
from pathlib import Path

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

import os
import io
import csv
import time
import uuid
import secrets
import hashlib
import random
import logging
import bcrypt
import jwt
from datetime import datetime, timezone, timedelta
from typing import List, Optional
from fastapi import FastAPI, APIRouter, HTTPException, Request, Depends
from fastapi.responses import StreamingResponse
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel, Field
from openpyxl import Workbook
from seed_data import TKJ_QUESTIONS, build_disc_items, DISC_INTERPRETATIONS

mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

JWT_SECRET = os.environ['JWT_SECRET']
JWT_ALGO = "HS256"
TOKEN_CHARSET = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"

app = FastAPI()
api = APIRouter(prefix="/api")
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("securecbt")


def now_utc():
    return datetime.now(timezone.utc)


def iso(dt):
    return dt.isoformat() if dt else None


def parse_dt(s):
    if isinstance(s, datetime):
        return s if s.tzinfo else s.replace(tzinfo=timezone.utc)
    return datetime.fromisoformat(s)


# ---------- Auth helpers ----------
def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def verify_password(plain: str, hashed: str) -> bool:
    return bcrypt.checkpw(plain.encode(), hashed.encode())


def create_access_token(admin_id: str, email: str) -> str:
    payload = {"sub": admin_id, "email": email, "type": "access",
               "exp": now_utc() + timedelta(hours=12)}
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGO)


async def get_current_admin(request: Request) -> dict:
    token = request.cookies.get("access_token")
    if not token:
        auth = request.headers.get("Authorization", "")
        if auth.startswith("Bearer "):
            token = auth[7:]
    if not token:
        raise HTTPException(401, "Not authenticated")
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGO])
        if payload.get("type") != "access":
            raise HTTPException(401, "Invalid token type")
        admin = await db.admins.find_one({"id": payload["sub"]}, {"_id": 0, "password_hash": 0})
        if not admin:
            raise HTTPException(401, "Admin not found")
        return admin
    except jwt.ExpiredSignatureError:
        raise HTTPException(401, "Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(401, "Invalid token")


# ---------- Config ----------
DEFAULT_CONFIG = {
    "id": "main",
    "tkj_duration_minutes": 60,
    "disc_duration_minutes": 20,
    "tkj_question_count": 25,
    "violation_threshold": 3,
    "require_seb": False,
    "seb_browser_exam_key": "",
}


async def get_config() -> dict:
    cfg = await db.exam_configs.find_one({"id": "main"}, {"_id": 0})
    if not cfg:
        await db.exam_configs.insert_one(dict(DEFAULT_CONFIG))
        cfg = dict(DEFAULT_CONFIG)
    return {**DEFAULT_CONFIG, **cfg}


# ---------- SEB verification ----------
async def verify_seb(request: Request):
    cfg = await get_config()
    if not cfg.get("require_seb"):
        return
    bek = cfg.get("seb_browser_exam_key", "")
    req_hash = request.headers.get("X-SafeExamBrowser-RequestHash", "")
    cfg_hash = request.headers.get("X-SafeExamBrowser-ConfigKeyHash", "")
    if not req_hash and not cfg_hash:
        raise HTTPException(403, "Ujian ini wajib menggunakan Safe Exam Browser (SEB)")
    if bek and req_hash:
        url = str(request.url).replace("http://", "https://", 1) if request.url.scheme == "http" else str(request.url)
        expected = hashlib.sha256((url + bek).encode()).hexdigest()
        expected_raw = hashlib.sha256((str(request.url) + bek).encode()).hexdigest()
        if req_hash.lower() not in (expected, expected_raw):
            raise HTTPException(403, "Verifikasi Browser Exam Key gagal")


# ---------- Rate limiting (in-memory) ----------
_rate: dict = {}


def rate_limit(ip: str, key: str, limit: int = 10, window: int = 60):
    bucket = f"{ip}:{key}"
    nowt = time.time()
    hits = [t for t in _rate.get(bucket, []) if nowt - t < window]
    if len(hits) >= limit:
        raise HTTPException(429, "Terlalu banyak percobaan, coba lagi sebentar lagi")
    hits.append(nowt)
    _rate[bucket] = hits


# ---------- Models ----------
class LoginBody(BaseModel):
    email: str
    password: str


class TokenGenBody(BaseModel):
    count: int = Field(ge=1, le=500)


class QuestionBody(BaseModel):
    text: str
    options: List[str] = Field(min_length=2, max_length=6)
    correct_index: int
    category: str = "Umum"
    difficulty: str = "sedang"


class DiscItemsBody(BaseModel):
    items: List[dict]


class ConfigBody(BaseModel):
    tkj_duration_minutes: int = Field(ge=1, le=600)
    disc_duration_minutes: int = Field(ge=1, le=600)
    tkj_question_count: int = Field(ge=1, le=200)
    violation_threshold: int = Field(ge=1, le=20)
    require_seb: bool
    seb_browser_exam_key: str = ""


class ExamStartBody(BaseModel):
    name: str = Field(min_length=2)
    school: str = Field(min_length=2)
    class_name: str = Field(min_length=1)
    token: str = Field(min_length=8, max_length=8)


class AnswerBody(BaseModel):
    participant_id: str
    token: str
    question_id: str
    selected_index: int


class SessionBody(BaseModel):
    participant_id: str
    token: str


class DiscAnswerBody(BaseModel):
    participant_id: str
    token: str
    group_index: int
    most: int
    least: int


class ViolationBody(BaseModel):
    participant_id: str
    token: str
    violation_type: str
    detail: str = ""


# ---------- Auth endpoints ----------
@api.post("/auth/login")
async def login(body: LoginBody, request: Request):
    email = body.email.strip().lower()
    ip = request.client.host if request.client else "unknown"
    ident = f"{ip}:{email}"
    attempt = await db.login_attempts.find_one({"identifier": ident})
    if attempt and attempt.get("count", 0) >= 5:
        locked_at = parse_dt(attempt["last_attempt"])
        if now_utc() - locked_at < timedelta(minutes=15):
            raise HTTPException(429, "Terlalu banyak percobaan gagal. Coba lagi dalam 15 menit.")
        await db.login_attempts.delete_one({"identifier": ident})
    admin = await db.admins.find_one({"email": email})
    if not admin or not verify_password(body.password, admin["password_hash"]):
        await db.login_attempts.update_one(
            {"identifier": ident},
            {"$inc": {"count": 1}, "$set": {"last_attempt": iso(now_utc())}},
            upsert=True)
        raise HTTPException(401, "Email atau password salah")
    await db.login_attempts.delete_one({"identifier": ident})
    token = create_access_token(admin["id"], email)
    return {"access_token": token, "user": {"id": admin["id"], "email": email, "name": admin.get("name", "Admin"), "role": "admin"}}


@api.get("/auth/me")
async def me(admin: dict = Depends(get_current_admin)):
    return admin


# ---------- Admin: Tokens ----------
def gen_token_code() -> str:
    return "".join(secrets.choice(TOKEN_CHARSET) for _ in range(8))


@api.post("/admin/tokens/generate")
async def generate_tokens(body: TokenGenBody, admin: dict = Depends(get_current_admin)):
    docs = []
    for _ in range(body.count):
        code = gen_token_code()
        while await db.tokens.find_one({"code": code}):
            code = gen_token_code()
        docs.append({"id": str(uuid.uuid4()), "code": code, "status": "unused",
                     "created_at": iso(now_utc()), "participant_id": None,
                     "activated_at": None, "completed_at": None})
    await db.tokens.insert_many([dict(d) for d in docs])
    return {"tokens": [{k: v for k, v in d.items() if k != "_id"} for d in docs]}


@api.get("/admin/tokens")
async def list_tokens(status: Optional[str] = None, admin: dict = Depends(get_current_admin)):
    q = {"status": status} if status else {}
    tokens = await db.tokens.find(q, {"_id": 0}).sort("created_at", -1).to_list(2000)
    pids = [t["participant_id"] for t in tokens if t.get("participant_id")]
    parts = await db.participants.find({"id": {"$in": pids}}, {"_id": 0, "id": 1, "name": 1}).to_list(2000)
    pmap = {p["id"]: p["name"] for p in parts}
    for t in tokens:
        t["participant_name"] = pmap.get(t.get("participant_id"))
    return tokens


@api.post("/admin/tokens/{token_id}/revoke")
async def revoke_token(token_id: str, admin: dict = Depends(get_current_admin)):
    res = await db.tokens.update_one({"id": token_id, "status": {"$in": ["unused", "active"]}},
                                     {"$set": {"status": "revoked"}})
    if res.matched_count == 0:
        raise HTTPException(404, "Token tidak ditemukan atau tidak bisa direvoke")
    return {"ok": True}


@api.get("/admin/tokens/export")
async def export_tokens(format: str = "csv", admin: dict = Depends(get_current_admin)):
    tokens = await db.tokens.find({}, {"_id": 0}).sort("created_at", -1).to_list(5000)
    headers = ["Token", "Status", "Dibuat", "Peserta ID"]
    rows = [[t["code"], t["status"], t["created_at"], t.get("participant_id") or ""] for t in tokens]
    return build_export(headers, rows, "tokens", format)


def build_export(headers, rows, name, fmt):
    if fmt == "xlsx":
        wb = Workbook()
        ws = wb.active
        ws.append(headers)
        for r in rows:
            ws.append(r)
        buf = io.BytesIO()
        wb.save(buf)
        buf.seek(0)
        return StreamingResponse(buf, media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                                 headers={"Content-Disposition": f"attachment; filename={name}.xlsx"})
    buf = io.StringIO()
    w = csv.writer(buf)
    w.writerow(headers)
    w.writerows(rows)
    return StreamingResponse(iter([buf.getvalue()]), media_type="text/csv",
                             headers={"Content-Disposition": f"attachment; filename={name}.csv"})


# ---------- Admin: Questions ----------
@api.get("/admin/questions")
async def list_questions(admin: dict = Depends(get_current_admin)):
    return await db.questions.find({}, {"_id": 0}).sort("created_at", 1).to_list(1000)


@api.post("/admin/questions")
async def create_question(body: QuestionBody, admin: dict = Depends(get_current_admin)):
    if body.correct_index >= len(body.options):
        raise HTTPException(400, "correct_index di luar jangkauan opsi")
    doc = {"id": str(uuid.uuid4()), **body.model_dump(), "created_at": iso(now_utc())}
    await db.questions.insert_one(dict(doc))
    doc.pop("_id", None)
    return doc


@api.put("/admin/questions/{qid}")
async def update_question(qid: str, body: QuestionBody, admin: dict = Depends(get_current_admin)):
    res = await db.questions.update_one({"id": qid}, {"$set": body.model_dump()})
    if res.matched_count == 0:
        raise HTTPException(404, "Soal tidak ditemukan")
    return {"ok": True}


@api.delete("/admin/questions/{qid}")
async def delete_question(qid: str, admin: dict = Depends(get_current_admin)):
    res = await db.questions.delete_one({"id": qid})
    if res.deleted_count == 0:
        raise HTTPException(404, "Soal tidak ditemukan")
    return {"ok": True}


@api.get("/admin/disc-items")
async def get_disc_items(admin: dict = Depends(get_current_admin)):
    return await db.disc_items.find({}, {"_id": 0}).sort("group_index", 1).to_list(100)


@api.put("/admin/disc-items")
async def update_disc_items(body: DiscItemsBody, admin: dict = Depends(get_current_admin)):
    await db.disc_items.delete_many({})
    items = []
    for i, item in enumerate(body.items):
        items.append({"group_index": i, "statements": item["statements"]})
    await db.disc_items.insert_many([dict(i) for i in items])
    return {"ok": True, "count": len(items)}


# ---------- Admin: Config ----------
@api.get("/admin/config")
async def read_config(admin: dict = Depends(get_current_admin)):
    return await get_config()


@api.put("/admin/config")
async def update_config(body: ConfigBody, admin: dict = Depends(get_current_admin)):
    await db.exam_configs.update_one({"id": "main"}, {"$set": body.model_dump()}, upsert=True)
    return await get_config()


# ---------- Admin: Results & stats ----------
async def participant_summary(p: dict) -> dict:
    vcount = await db.violation_logs.count_documents({"participant_id": p["id"]})
    disc = p.get("disc_result") or {}
    return {
        "id": p["id"], "name": p["name"], "school": p["school"], "class_name": p["class_name"],
        "token_code": p["token_code"], "stage": p["stage"],
        "tkj_score": p.get("tkj_score"), "tkj_total": p.get("tkj_total"),
        "disc_dominant": disc.get("dominant"), "violation_count": vcount,
        "auto_submitted": p.get("auto_submitted", False),
        "created_at": p.get("created_at"), "completed_at": p.get("completed_at"),
    }


@api.get("/admin/results")
async def list_results(admin: dict = Depends(get_current_admin)):
    parts = await db.participants.find({}, {"_id": 0}).sort("created_at", -1).to_list(2000)
    return [await participant_summary(p) for p in parts]


@api.get("/admin/results/export")
async def export_results(format: str = "csv", admin: dict = Depends(get_current_admin)):
    parts = await db.participants.find({}, {"_id": 0}).sort("created_at", -1).to_list(5000)
    headers = ["Nama", "Sekolah", "Kelas", "Token", "Status", "Skor TKJ", "Total Soal", "Persentase",
               "DISC D", "DISC I", "DISC S", "DISC C", "Profil Dominan", "Pelanggaran", "Auto Submit", "Selesai"]
    rows = []
    for p in parts:
        s = await participant_summary(p)
        disc = p.get("disc_result") or {}
        change = disc.get("change", {})
        pct = round(100 * (s["tkj_score"] or 0) / s["tkj_total"], 1) if s.get("tkj_total") else ""
        rows.append([s["name"], s["school"], s["class_name"], s["token_code"], s["stage"],
                     s["tkj_score"] if s["tkj_score"] is not None else "", s["tkj_total"] or "", pct,
                     change.get("D", ""), change.get("I", ""), change.get("S", ""), change.get("C", ""),
                     s["disc_dominant"] or "", s["violation_count"],
                     "Ya" if s["auto_submitted"] else "Tidak", s["completed_at"] or ""])
    return build_export(headers, rows, "hasil_ujian", format)


@api.get("/admin/results/{pid}")
async def result_detail(pid: str, admin: dict = Depends(get_current_admin)):
    p = await db.participants.find_one({"id": pid}, {"_id": 0})
    if not p:
        raise HTTPException(404, "Peserta tidak ditemukan")
    violations = await db.violation_logs.find({"participant_id": pid}, {"_id": 0}).sort("timestamp", 1).to_list(500)
    summary = await participant_summary(p)
    return {**summary, "disc_result": p.get("disc_result"), "violations": violations,
            "tkj_answers": p.get("tkj_answers", {}), "tkj_started_at": p.get("tkj_started_at")}


@api.get("/admin/stats")
async def stats(admin: dict = Depends(get_current_admin)):
    total_tokens = await db.tokens.count_documents({})
    by_status = {}
    for s in ["unused", "active", "completed", "expired", "revoked"]:
        by_status[s] = await db.tokens.count_documents({"status": s})
    participants = await db.participants.count_documents({})
    completed = await db.participants.count_documents({"stage": "done"})
    questions = await db.questions.count_documents({})
    violations = await db.violation_logs.count_documents({})
    scores = await db.participants.find({"tkj_score": {"$ne": None}}, {"_id": 0, "tkj_score": 1, "tkj_total": 1}).to_list(2000)
    avg = round(sum(100 * s["tkj_score"] / s["tkj_total"] for s in scores if s.get("tkj_total")) / len(scores), 1) if scores else 0
    return {"tokens": {"total": total_tokens, **by_status}, "participants": participants,
            "completed": completed, "questions": questions, "violations": violations, "avg_score_pct": avg}


# ---------- Exam helpers ----------
async def get_session(participant_id: str, token_code: str) -> tuple:
    p = await db.participants.find_one({"id": participant_id}, {"_id": 0})
    if not p or p["token_code"] != token_code.upper():
        raise HTTPException(404, "Sesi tidak ditemukan")
    t = await db.tokens.find_one({"code": token_code.upper()}, {"_id": 0})
    if not t:
        raise HTTPException(404, "Token tidak ditemukan")
    if t["status"] in ("completed", "expired", "revoked"):
        raise HTTPException(403, "Token sudah tidak berlaku")
    return p, t


def remaining_seconds(started_at: str, duration_minutes: int) -> int:
    elapsed = (now_utc() - parse_dt(started_at)).total_seconds()
    return max(0, int(duration_minutes * 60 - elapsed))


async def tkj_questions_for(p: dict) -> list:
    qids = [o["qid"] for o in p["question_order"]]
    qdocs = await db.questions.find({"id": {"$in": qids}}, {"_id": 0}).to_list(500)
    qmap = {q["id"]: q for q in qdocs}
    out = []
    for o in p["question_order"]:
        q = qmap.get(o["qid"])
        if not q:
            continue
        out.append({"id": q["id"], "text": q["text"], "category": q.get("category", ""),
                    "options": [q["options"][i] for i in o["option_order"]]})
    return out


def display_answers(p: dict) -> dict:
    omap = {o["qid"]: o["option_order"] for o in p["question_order"]}
    out = {}
    for qid, orig in p.get("tkj_answers", {}).items():
        order = omap.get(qid)
        if order is not None and orig in order:
            out[qid] = order.index(orig)
    return out


async def score_tkj(p: dict) -> int:
    qids = [o["qid"] for o in p["question_order"]]
    qdocs = await db.questions.find({"id": {"$in": qids}}, {"_id": 0, "id": 1, "correct_index": 1}).to_list(500)
    correct = {q["id"]: q["correct_index"] for q in qdocs}
    return sum(1 for qid, ans in p.get("tkj_answers", {}).items() if correct.get(qid) == ans)


async def do_submit_tkj(p: dict, auto: bool = False) -> dict:
    score = await score_tkj(p)
    update = {"tkj_score": score, "tkj_total": len(p["question_order"]),
              "tkj_submitted_at": iso(now_utc()), "stage": "disc",
              "disc_started_at": iso(now_utc())}
    if auto:
        update["auto_submitted"] = True
    await db.participants.update_one({"id": p["id"]}, {"$set": update})
    return update


async def compute_disc(p: dict) -> dict:
    items = await db.disc_items.find({}, {"_id": 0}).sort("group_index", 1).to_list(100)
    most = {"D": 0, "I": 0, "S": 0, "C": 0}
    least = {"D": 0, "I": 0, "S": 0, "C": 0}
    for item in items:
        ans = p.get("disc_answers", {}).get(str(item["group_index"]))
        if not ans:
            continue
        stmts = item["statements"]
        if 0 <= ans["most"] < len(stmts):
            most[stmts[ans["most"]]["dimension"]] += 1
        if 0 <= ans["least"] < len(stmts):
            least[stmts[ans["least"]]["dimension"]] += 1
    change = {d: most[d] - least[d] for d in "DISC"}
    dominant = max(change, key=lambda d: change[d])
    return {"most": most, "least": least, "change": change, "dominant": dominant,
            "interpretation": DISC_INTERPRETATIONS[dominant],
            "answered_groups": len(p.get("disc_answers", {})), "total_groups": len(items)}


async def do_complete(p: dict, auto: bool = False) -> dict:
    disc = await compute_disc(p)
    update = {"disc_result": disc, "stage": "done", "completed_at": iso(now_utc())}
    if auto:
        update["auto_submitted"] = True
    await db.participants.update_one({"id": p["id"]}, {"$set": update})
    await db.tokens.update_one({"code": p["token_code"]},
                               {"$set": {"status": "completed", "completed_at": iso(now_utc())}})
    return update


async def build_state(p: dict, t: dict, cfg: dict) -> dict:
    p = await db.participants.find_one({"id": p["id"]}, {"_id": 0})
    state = {"participant_id": p["id"], "name": p["name"], "stage": p["stage"],
             "violation_count": await db.violation_logs.count_documents({"participant_id": p["id"]}),
             "violation_threshold": cfg["violation_threshold"]}
    if p["stage"] == "tkj":
        rem = remaining_seconds(p["tkj_started_at"], cfg["tkj_duration_minutes"])
        if rem <= 0:
            await do_submit_tkj(p, auto=False)
            return await build_state(p, t, cfg)
        state.update({"questions": await tkj_questions_for(p), "answers": display_answers(p),
                      "remaining_seconds": rem})
    elif p["stage"] == "disc":
        rem = remaining_seconds(p["disc_started_at"], cfg["disc_duration_minutes"])
        if rem <= 0:
            await do_complete(p, auto=False)
            return await build_state(p, t, cfg)
        items = await db.disc_items.find({}, {"_id": 0}).sort("group_index", 1).to_list(100)
        state.update({"disc_items": [{"group_index": i["group_index"],
                                      "statements": [s["text"] for s in i["statements"]]} for i in items],
                      "disc_answers": p.get("disc_answers", {}), "remaining_seconds": rem})
    return state


# ---------- Exam endpoints (participant) ----------
@api.get("/exam/seb-status")
async def seb_status(request: Request):
    cfg = await get_config()
    ua = request.headers.get("User-Agent", "")
    has_seb_header = bool(request.headers.get("X-SafeExamBrowser-RequestHash") or
                          request.headers.get("X-SafeExamBrowser-ConfigKeyHash"))
    return {"require_seb": cfg["require_seb"],
            "seb_detected": has_seb_header or "SEB" in ua}


@api.post("/exam/start", dependencies=[Depends(verify_seb)])
async def exam_start(body: ExamStartBody, request: Request):
    rate_limit(request.client.host if request.client else "x", "start", limit=10, window=60)
    code = body.token.strip().upper()
    t = await db.tokens.find_one({"code": code}, {"_id": 0})
    if not t:
        raise HTTPException(404, "Token tidak valid")
    cfg = await get_config()
    if t["status"] == "active":
        p = await db.participants.find_one({"id": t["participant_id"]}, {"_id": 0})
        if not p:
            raise HTTPException(500, "Data sesi rusak, hubungi admin")
        window_min = cfg["tkj_duration_minutes"] + cfg["disc_duration_minutes"] + 10
        if remaining_seconds(p["tkj_started_at"], window_min) <= 0:
            await db.tokens.update_one({"code": code}, {"$set": {"status": "expired"}})
            raise HTTPException(403, "Sesi sudah kedaluwarsa")
        return await build_state(p, t, cfg)
    if t["status"] != "unused":
        raise HTTPException(403, "Token sudah digunakan atau tidak berlaku")
    qcount = await db.questions.count_documents({})
    if qcount == 0:
        raise HTTPException(500, "Bank soal kosong, hubungi admin")
    qdocs = await db.questions.find({}, {"_id": 0, "id": 1, "options": 1}).to_list(1000)
    random.shuffle(qdocs)
    selected = qdocs[:cfg["tkj_question_count"]]
    order = []
    for q in selected:
        opt_order = list(range(len(q["options"])))
        random.shuffle(opt_order)
        order.append({"qid": q["id"], "option_order": opt_order})
    pid = str(uuid.uuid4())
    p = {"id": pid, "name": body.name.strip(), "school": body.school.strip(),
         "class_name": body.class_name.strip(), "token_code": code, "stage": "tkj",
         "question_order": order, "tkj_answers": {}, "tkj_score": None, "tkj_total": None,
         "tkj_started_at": iso(now_utc()), "tkj_submitted_at": None,
         "disc_answers": {}, "disc_started_at": None, "disc_result": None,
         "auto_submitted": False, "created_at": iso(now_utc()), "completed_at": None}
    await db.participants.insert_one(dict(p))
    await db.tokens.update_one({"code": code},
                               {"$set": {"status": "active", "participant_id": pid, "activated_at": iso(now_utc())}})
    return await build_state(p, t, cfg)


@api.post("/exam/session", dependencies=[Depends(verify_seb)])
async def exam_session(body: SessionBody):
    p, t = await get_session(body.participant_id, body.token)
    return await build_state(p, t, await get_config())


@api.post("/exam/answer", dependencies=[Depends(verify_seb)])
async def exam_answer(body: AnswerBody):
    p, t = await get_session(body.participant_id, body.token)
    if p["stage"] != "tkj":
        raise HTTPException(400, "Sesi TKJ sudah berakhir")
    cfg = await get_config()
    rem = remaining_seconds(p["tkj_started_at"], cfg["tkj_duration_minutes"])
    if rem <= 0:
        await do_submit_tkj(p)
        return {"saved": False, "stage": "disc", "remaining_seconds": 0}
    omap = {o["qid"]: o["option_order"] for o in p["question_order"]}
    order = omap.get(body.question_id)
    if order is None or not (0 <= body.selected_index < len(order)):
        raise HTTPException(400, "Jawaban tidak valid")
    original = order[body.selected_index]
    await db.participants.update_one({"id": p["id"]},
                                     {"$set": {f"tkj_answers.{body.question_id}": original}})
    return {"saved": True, "stage": "tkj", "remaining_seconds": rem}


@api.post("/exam/tkj/submit", dependencies=[Depends(verify_seb)])
async def tkj_submit(body: SessionBody):
    p, t = await get_session(body.participant_id, body.token)
    if p["stage"] != "tkj":
        raise HTTPException(400, "TKJ sudah disubmit")
    await do_submit_tkj(p)
    return await build_state(p, t, await get_config())


@api.post("/exam/disc/answer", dependencies=[Depends(verify_seb)])
async def disc_answer(body: DiscAnswerBody):
    p, t = await get_session(body.participant_id, body.token)
    if p["stage"] != "disc":
        raise HTTPException(400, "Sesi DISC tidak aktif")
    if body.most == body.least:
        raise HTTPException(400, "'Paling' dan 'Kurang' tidak boleh sama")
    cfg = await get_config()
    rem = remaining_seconds(p["disc_started_at"], cfg["disc_duration_minutes"])
    if rem <= 0:
        await do_complete(p)
        return {"saved": False, "stage": "done", "remaining_seconds": 0}
    await db.participants.update_one({"id": p["id"]},
                                     {"$set": {f"disc_answers.{body.group_index}": {"most": body.most, "least": body.least}}})
    return {"saved": True, "stage": "disc", "remaining_seconds": rem}


@api.post("/exam/disc/submit", dependencies=[Depends(verify_seb)])
async def disc_submit(body: SessionBody):
    p, t = await get_session(body.participant_id, body.token)
    if p["stage"] != "disc":
        raise HTTPException(400, "Sesi DISC tidak aktif")
    p = await db.participants.find_one({"id": p["id"]}, {"_id": 0})
    await do_complete(p)
    return {"stage": "done"}


@api.post("/exam/violation")
async def log_violation(body: ViolationBody):
    p, t = await get_session(body.participant_id, body.token)
    if p["stage"] == "done":
        return {"logged": False, "stage": "done"}
    await db.violation_logs.insert_one({
        "id": str(uuid.uuid4()), "participant_id": p["id"], "token_code": p["token_code"],
        "violation_type": body.violation_type, "detail": body.detail,
        "stage": p["stage"], "timestamp": iso(now_utc())})
    cfg = await get_config()
    count = await db.violation_logs.count_documents({
        "participant_id": p["id"],
        "violation_type": {"$in": ["tab-switch", "fullscreen-exit"]}})
    auto_submit = count >= cfg["violation_threshold"]
    if auto_submit:
        p = await db.participants.find_one({"id": p["id"]}, {"_id": 0})
        if p["stage"] == "tkj":
            await do_submit_tkj(p, auto=True)
            p = await db.participants.find_one({"id": p["id"]}, {"_id": 0})
        if p["stage"] == "disc":
            await do_complete(p, auto=True)
        return {"logged": True, "count": count, "auto_submitted": True, "stage": "done"}
    return {"logged": True, "count": count, "auto_submitted": False,
            "remaining_warnings": cfg["violation_threshold"] - count}


# ---------- Startup ----------
@app.on_event("startup")
async def startup():
    await db.admins.create_index("email", unique=True)
    await db.tokens.create_index("code", unique=True)
    await db.participants.create_index("id")
    await db.violation_logs.create_index("participant_id")
    await db.login_attempts.create_index("identifier")
    email = os.environ["ADMIN_EMAIL"].lower()
    password = os.environ["ADMIN_PASSWORD"]
    existing = await db.admins.find_one({"email": email})
    if not existing:
        await db.admins.insert_one({"id": str(uuid.uuid4()), "email": email, "name": "Admin",
                                    "role": "admin", "password_hash": hash_password(password),
                                    "created_at": iso(now_utc())})
    elif not verify_password(password, existing["password_hash"]):
        await db.admins.update_one({"email": email}, {"$set": {"password_hash": hash_password(password)}})
    if await db.questions.count_documents({}) == 0:
        docs = [{"id": str(uuid.uuid4()), **q, "created_at": iso(now_utc())} for q in TKJ_QUESTIONS]
        await db.questions.insert_many(docs)
        logger.info(f"Seeded {len(docs)} TKJ questions")
    if await db.disc_items.count_documents({}) == 0:
        await db.disc_items.insert_many(build_disc_items())
        logger.info("Seeded 24 DISC groups")
    await get_config()


app.include_router(api)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
