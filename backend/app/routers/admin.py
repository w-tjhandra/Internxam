import io
import json
import uuid
from typing import Optional

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile

from app import runtime as shared
from app.schemas.admin import ConfigBody, DiscItemsBody, QuestionBody, TokenGenBody
from app.seed_data import (
    SCENARIO_ASSESSMENT_DISCLAIMER,
    SCENARIO_ASSESSMENT_VERSION,
    SCENARIO_INDICATORS,
    SCENARIO_ITEMS,
)


router = APIRouter()


@router.post("/admin/tokens/generate")
async def generate_tokens(
    body: TokenGenBody, admin: dict = Depends(shared.get_current_admin)
):
    docs = []
    async with shared.pool.acquire() as conn:
        for _ in range(body.count):
            while True:
                code = shared.gen_token_code()
                if not await conn.fetchval(
                    "SELECT 1 FROM tokens WHERE code = $1", code
                ):
                    break
            doc = {
                "id": str(uuid.uuid4()),
                "code": code,
                "status": "unused",
                "created_at": shared.now_utc(),
                "participant_id": None,
                "activated_at": None,
                "completed_at": None,
                "type": body.type,
                "max_uses": body.max_uses,
                "usage_count": 0,
            }
            docs.append(doc)
            await conn.execute(
                """INSERT INTO tokens
                   (id, code, status, created_at, type, max_uses, usage_count)
                   VALUES ($1, $2, $3, $4, $5, $6, $7)""",
                doc["id"],
                doc["code"],
                doc["status"],
                doc["created_at"],
                doc["type"],
                doc["max_uses"],
                doc["usage_count"],
            )
    for doc in docs:
        doc["created_at"] = shared.iso(doc["created_at"])
    return {"tokens": docs}


@router.get("/admin/tokens")
async def list_tokens(
    status: Optional[str] = None, admin: dict = Depends(shared.get_current_admin)
):
    async with shared.pool.acquire() as conn:
        query = (
            "SELECT t.*, p.name as participant_name FROM tokens t "
            "LEFT JOIN participants p ON t.participant_id = p.id"
        )
        if status:
            tokens = await conn.fetch(
                query + " WHERE t.status = $1 ORDER BY t.created_at DESC LIMIT 2000",
                status,
            )
        else:
            tokens = await conn.fetch(
                query + " ORDER BY t.created_at DESC LIMIT 2000"
            )
        return [dict(token) for token in tokens]


@router.post("/admin/tokens/{token_id}/revoke")
async def revoke_token(
    token_id: str, admin: dict = Depends(shared.get_current_admin)
):
    async with shared.pool.acquire() as conn:
        result = await conn.execute(
            """UPDATE tokens SET status = 'revoked'
               WHERE id = $1 AND status IN ('unused', 'active')""",
            token_id,
        )
        if result == "UPDATE 0":
            raise HTTPException(404, "Token tidak ditemukan atau tidak bisa direvoke")
        return {"ok": True}


@router.get("/admin/tokens/export")
async def export_tokens(
    format: str = "csv", admin: dict = Depends(shared.get_current_admin)
):
    async with shared.pool.acquire() as conn:
        tokens = await conn.fetch(
            "SELECT * FROM tokens ORDER BY created_at DESC LIMIT 5000"
        )
        rows = [
            [
                token["code"],
                token["status"],
                shared.iso(token["created_at"]),
                token.get("participant_id") or "",
            ]
            for token in tokens
        ]
        return shared.build_export(
            ["Token", "Status", "Dibuat", "Peserta ID"], rows, "tokens", format
        )


@router.get("/admin/questions")
async def list_questions(admin: dict = Depends(shared.get_current_admin)):
    async with shared.pool.acquire() as conn:
        questions = await conn.fetch(
            "SELECT * FROM questions ORDER BY created_at ASC"
        )
        return [
            dict(question, options=json.loads(question["options"]))
            for question in questions
        ]


@router.post("/admin/questions")
async def create_question(
    body: QuestionBody, admin: dict = Depends(shared.get_current_admin)
):
    if body.correct_index >= len(body.options):
        raise HTTPException(400, "correct_index di luar jangkauan")
    doc = {"id": str(uuid.uuid4()), **body.model_dump(), "created_at": shared.now_utc()}
    async with shared.pool.acquire() as conn:
        await conn.execute(
            """INSERT INTO questions
               (id, text, options, correct_index, category, difficulty, created_at)
               VALUES ($1, $2, $3, $4, $5, $6, $7)""",
            doc["id"],
            doc["text"],
            json.dumps(doc["options"]),
            doc["correct_index"],
            doc["category"],
            doc["difficulty"],
            doc["created_at"],
        )
    doc["options"] = body.options
    doc["created_at"] = shared.iso(doc["created_at"])
    return doc


@router.post("/admin/questions/import")
async def import_questions(
    file: UploadFile = File(...), admin: dict = Depends(shared.get_current_admin)
):
    import pandas as pd

    content = await file.read()
    if file.filename.endswith(".csv"):
        dataframe = pd.read_csv(io.BytesIO(content))
    else:
        dataframe = pd.read_excel(io.BytesIO(content))
    count = 0
    async with shared.pool.acquire() as conn:
        for _, row in dataframe.iterrows():
            if pd.isna(row.get("text")):
                continue
            options = [
                str(row.get(f"option_{letter}", ""))
                for letter in ["a", "b", "c", "d", "e"]
                if f"option_{letter}" in row
                and not pd.isna(row.get(f"option_{letter}"))
            ]
            if len(options) < 2:
                continue
            correct_letter = str(row.get("correct_option", "A")).strip().upper()
            correct_index = ord(correct_letter) - 65
            if not 0 <= correct_index < len(options):
                correct_index = 0
            doc = {
                "id": str(uuid.uuid4()),
                "text": str(row["text"]),
                "options": options,
                "correct_index": correct_index,
                "category": str(row.get("category", "Umum")),
                "difficulty": str(row.get("difficulty", "sedang")),
                "created_at": shared.now_utc(),
            }
            await conn.execute(
                """INSERT INTO questions
                   (id, text, options, correct_index, category, difficulty, created_at)
                   VALUES ($1, $2, $3, $4, $5, $6, $7)""",
                doc["id"],
                doc["text"],
                json.dumps(doc["options"]),
                doc["correct_index"],
                doc["category"],
                doc["difficulty"],
                doc["created_at"],
            )
            count += 1
    return {"ok": True, "count": count}


@router.put("/admin/questions/{qid}")
async def update_question(
    qid: str, body: QuestionBody, admin: dict = Depends(shared.get_current_admin)
):
    async with shared.pool.acquire() as conn:
        result = await conn.execute(
            """UPDATE questions SET text=$1, options=$2, correct_index=$3,
               category=$4, difficulty=$5 WHERE id=$6""",
            body.text,
            json.dumps(body.options),
            body.correct_index,
            body.category,
            body.difficulty,
            qid,
        )
        if result == "UPDATE 0":
            raise HTTPException(404, "Soal tidak ditemukan")
        return {"ok": True}


@router.delete("/admin/questions/{qid}")
async def delete_question(
    qid: str, admin: dict = Depends(shared.get_current_admin)
):
    async with shared.pool.acquire() as conn:
        result = await conn.execute("DELETE FROM questions WHERE id = $1", qid)
        if result == "DELETE 0":
            raise HTTPException(404, "Soal tidak ditemukan")
        return {"ok": True}


@router.get("/admin/disc-items")
async def get_disc_items(admin: dict = Depends(shared.get_current_admin)):
    async with shared.pool.acquire() as conn:
        items = await conn.fetch(
            "SELECT * FROM disc_items ORDER BY group_index ASC"
        )
        return [
            dict(item, statements=json.loads(item["statements"])) for item in items
        ]


@router.put("/admin/disc-items")
async def update_disc_items(
    body: DiscItemsBody, admin: dict = Depends(shared.get_current_admin)
):
    async with shared.pool.acquire() as conn:
        await conn.execute("DELETE FROM disc_items")
        for index, item in enumerate(body.items):
            await conn.execute(
                "INSERT INTO disc_items (group_index, statements) VALUES ($1, $2)",
                index,
                json.dumps(item["statements"]),
            )
    return {"ok": True, "count": len(body.items)}


@router.get("/admin/scenario-items")
async def get_scenario_items(admin: dict = Depends(shared.get_current_admin)):
    return {
        "version": SCENARIO_ASSESSMENT_VERSION,
        "status": "pilot",
        "disclaimer": SCENARIO_ASSESSMENT_DISCLAIMER,
        "indicators": SCENARIO_INDICATORS,
        "items": SCENARIO_ITEMS,
    }


@router.get("/admin/config")
async def read_config(admin: dict = Depends(shared.get_current_admin)):
    return await shared.get_config()


@router.put("/admin/config")
async def update_config(
    body: ConfigBody, admin: dict = Depends(shared.get_current_admin)
):
    async with shared.pool.acquire() as conn:
        await conn.execute(
            """UPDATE exam_configs SET tkj_duration_minutes=$1,
               disc_duration_minutes=$2, tkj_question_count=$3,
               violation_threshold=$4, require_seb=$5, seb_browser_exam_key=$6,
               work_disc_enabled=$7, work_disc_duration_minutes=$8
               WHERE id='main'""",
            body.tkj_duration_minutes,
            body.disc_duration_minutes,
            body.tkj_question_count,
            body.violation_threshold,
            body.require_seb,
            body.seb_browser_exam_key,
            body.work_disc_enabled,
            body.work_disc_duration_minutes,
        )
    return await shared.get_config()


@router.get("/admin/stats")
async def stats(admin: dict = Depends(shared.get_current_admin)):
    async with shared.pool.acquire() as conn:
        total_tokens = await conn.fetchval("SELECT COUNT(*) FROM tokens")
        by_status = {}
        for status in ["unused", "active", "completed", "expired", "revoked"]:
            by_status[status] = await conn.fetchval(
                "SELECT COUNT(*) FROM tokens WHERE status = $1", status
            )
        participants = await conn.fetchval("SELECT COUNT(*) FROM participants")
        completed = await conn.fetchval(
            "SELECT COUNT(*) FROM participants WHERE stage = 'done'"
        )
        questions = await conn.fetchval("SELECT COUNT(*) FROM questions")
        violations = await conn.fetchval("SELECT COUNT(*) FROM violation_logs")
        scores = await conn.fetch(
            """SELECT tkj_score, tkj_total FROM participants
               WHERE tkj_score IS NOT NULL"""
        )
        average = (
            round(
                sum(
                    100 * score["tkj_score"] / score["tkj_total"]
                    for score in scores
                    if score.get("tkj_total")
                )
                / len(scores),
                1,
            )
            if scores
            else 0
        )
        return {
            "tokens": {"total": total_tokens, **by_status},
            "participants": participants,
            "completed": completed,
            "questions": questions,
            "violations": violations,
            "avg_score_pct": average,
        }
