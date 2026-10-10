import json
import random
import uuid

from fastapi import APIRouter, Depends, HTTPException, Request

from app import runtime as shared
from app.schemas.exam import (
    AnswerBody,
    DiscAnswerBody,
    ExamStartBody,
    ScenarioAnswerBody,
    SessionBody,
    ViolationBody,
    WorkDiscAnswerBody,
)
from app.services import exam_workflow as workflow
from app.seed_data import SCENARIO_ITEMS


router = APIRouter()


@router.get("/exam/seb-status")
async def seb_status(request: Request):
    config = await shared.get_config()
    user_agent = request.headers.get("User-Agent", "")
    has_seb = bool(
        request.headers.get("X-SafeExamBrowser-RequestHash")
        or request.headers.get("X-SafeExamBrowser-ConfigKeyHash")
    )
    return {
        "require_seb": config["require_seb"],
        "seb_detected": has_seb or "SEB" in user_agent,
    }


@router.post(
    "/exam/start", dependencies=[Depends(shared.verify_seb)]
)
async def exam_start(body: ExamStartBody, request: Request):
    shared.rate_limit(
        request.client.host if request.client else "x",
        "start",
        limit=10,
        window=60,
    )
    code = body.token.strip().upper()
    async with shared.pool.acquire() as conn:
        token = await conn.fetchrow("SELECT * FROM tokens WHERE code = $1", code)
        if not token:
            raise HTTPException(404, "Token tidak valid")
        token = dict(token)
        config = await shared.get_config()

        existing = await conn.fetchrow(
            "SELECT * FROM participants WHERE token_code = $1 AND name = $2",
            code,
            body.name.strip(),
        )
        if existing:
            participant = dict(existing)
            window_minutes = (
                config["tkj_duration_minutes"]
                + config["disc_duration_minutes"]
                + config["work_disc_duration_minutes"]
                + 10
            )
            if (
                workflow.remaining_seconds(
                    participant["tkj_started_at"], window_minutes
                )
                <= 0
            ):
                raise HTTPException(403, "Sesi sudah kedaluwarsa")
            return await workflow.build_state(participant, token, config)

        if token["status"] in ("completed", "expired", "revoked"):
            raise HTTPException(403, "Token sudah tidak berlaku")
        if token["status"] == "active" and token.get("type") != "group":
            raise HTTPException(403, "Token single sudah digunakan oleh orang lain")
        if (
            token.get("type") == "group"
            and token.get("usage_count", 0) >= token.get("max_uses", 1)
        ):
            raise HTTPException(403, "Kapasitas token group sudah penuh")

        questions = await conn.fetch("SELECT id, options FROM questions")
        if not questions:
            raise HTTPException(500, "Bank soal kosong, hubungi admin")
        questions = [dict(question) for question in questions]
        random.shuffle(questions)
        order = []
        for question in questions[: config["tkj_question_count"]]:
            option_order = list(range(len(json.loads(question["options"]))))
            random.shuffle(option_order)
            order.append(
                {"qid": question["id"], "option_order": option_order}
            )
        participant_id = str(uuid.uuid4())
        participant = {
            "id": participant_id,
            "name": body.name.strip(),
            "school": body.school.strip(),
            "class_name": body.class_name.strip(),
            "token_code": code,
            "stage": "tkj",
            "question_order": json.dumps(order),
            "tkj_answers": "{}",
            "tkj_score": None,
            "tkj_total": None,
            "tkj_started_at": shared.now_utc(),
            "tkj_submitted_at": None,
            "disc_answers": "{}",
            "disc_started_at": None,
            "disc_result": None,
            "auto_submitted": False,
            "created_at": shared.now_utc(),
            "completed_at": None,
        }
        await conn.execute(
            """INSERT INTO participants
               (id, name, school, class_name, token_code, stage,
                question_order, tkj_answers, tkj_started_at, disc_answers,
                auto_submitted, created_at)
               VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12)""",
            participant["id"],
            participant["name"],
            participant["school"],
            participant["class_name"],
            participant["token_code"],
            participant["stage"],
            participant["question_order"],
            participant["tkj_answers"],
            participant["tkj_started_at"],
            participant["disc_answers"],
            participant["auto_submitted"],
            participant["created_at"],
        )
        usage_count = token.get("usage_count", 0) + 1
        await conn.execute(
            """UPDATE tokens SET status = 'active', participant_id = $1,
               activated_at = $2, usage_count = $3 WHERE code = $4""",
            participant_id,
            shared.now_utc(),
            usage_count,
            code,
        )
        await shared.manager.broadcast(
            {
                "type": "exam_start",
                "participant": participant["name"],
                "detail": "memulai ujian TKJ",
            }
        )
    return await workflow.build_state(participant, token, config)


@router.post(
    "/exam/session", dependencies=[Depends(shared.verify_seb)]
)
async def exam_session(body: SessionBody):
    participant, token = await workflow.get_session(
        body.participant_id, body.token
    )
    return await workflow.build_state(
        participant, token, await shared.get_config()
    )


@router.post(
    "/exam/answer", dependencies=[Depends(shared.verify_seb)]
)
async def exam_answer(body: AnswerBody):
    participant, _ = await workflow.get_session(
        body.participant_id, body.token
    )
    if participant["stage"] != "tkj":
        raise HTTPException(400, "Sesi TKJ sudah berakhir")
    config = await shared.get_config()
    remaining = workflow.remaining_seconds(
        participant["tkj_started_at"], config["tkj_duration_minutes"]
    )
    if remaining <= 0:
        await workflow.do_submit_tkj(participant)
        return {"saved": False, "stage": "scenario", "remaining_seconds": 0}
    order = json.loads(participant.get("question_order") or "[]")
    option_orders = {item["qid"]: item["option_order"] for item in order}
    option_order = option_orders.get(body.question_id)
    if option_order is None or not 0 <= body.selected_index < len(option_order):
        raise HTTPException(400, "Jawaban tidak valid")
    answers = json.loads(participant.get("tkj_answers") or "{}")
    answers[body.question_id] = option_order[body.selected_index]
    async with shared.pool.acquire() as conn:
        await conn.execute(
            "UPDATE participants SET tkj_answers = $1 WHERE id = $2",
            json.dumps(answers),
            participant["id"],
        )
    return {"saved": True, "stage": "tkj", "remaining_seconds": remaining}


@router.post(
    "/exam/tkj/submit", dependencies=[Depends(shared.verify_seb)]
)
async def tkj_submit(body: SessionBody):
    participant, token = await workflow.get_session(
        body.participant_id, body.token
    )
    if participant["stage"] != "tkj":
        raise HTTPException(400, "TKJ sudah disubmit")
    await workflow.do_submit_tkj(participant)
    await shared.manager.broadcast(
        {
            "type": "exam_submit",
            "participant": participant["name"],
            "detail": "menyelesaikan TKJ",
        }
    )
    return await workflow.build_state(
        participant, token, await shared.get_config()
    )


@router.post(
    "/exam/disc/answer", dependencies=[Depends(shared.verify_seb)]
)
async def disc_answer(body: DiscAnswerBody):
    participant, _ = await workflow.get_session(
        body.participant_id, body.token
    )
    if participant["stage"] != "disc":
        raise HTTPException(400, "Sesi DISC tidak aktif")
    if body.most == body.least:
        raise HTTPException(400, "'Paling' dan 'Kurang' tidak boleh sama")
    config = await shared.get_config()
    remaining = workflow.remaining_seconds(
        participant["disc_started_at"], config["disc_duration_minutes"]
    )
    if remaining <= 0:
        await workflow.do_complete(participant)
        return {"saved": False, "stage": "done", "remaining_seconds": 0}
    answers = json.loads(participant.get("disc_answers") or "{}")
    answers[str(body.group_index)] = {
        "most": body.most,
        "least": body.least,
    }
    async with shared.pool.acquire() as conn:
        await conn.execute(
            "UPDATE participants SET disc_answers = $1 WHERE id = $2",
            json.dumps(answers),
            participant["id"],
        )
    return {"saved": True, "stage": "disc", "remaining_seconds": remaining}


@router.post(
    "/exam/disc/submit", dependencies=[Depends(shared.verify_seb)]
)
async def disc_submit(body: SessionBody):
    participant, _ = await workflow.get_session(
        body.participant_id, body.token
    )
    if participant["stage"] != "disc":
        raise HTTPException(400, "Sesi DISC tidak aktif")
    async with shared.pool.acquire() as conn:
        participant = dict(
            await conn.fetchrow(
                "SELECT * FROM participants WHERE id = $1",
                participant["id"],
            )
        )
    await workflow.do_complete(participant)
    return {"stage": "done"}


@router.post(
    "/exam/scenario/answer", dependencies=[Depends(shared.verify_seb)]
)
async def scenario_answer(body: ScenarioAnswerBody):
    participant, token = await workflow.get_session(
        body.participant_id, body.token
    )
    if participant["stage"] != "scenario":
        raise HTTPException(400, "Sesi asesmen skenario tidak aktif")
    config = await shared.get_config()
    remaining = workflow.remaining_seconds(
        participant["scenario_started_at"], config["disc_duration_minutes"]
    )
    if remaining <= 0:
        await workflow.do_complete(participant, auto=True)
        return await workflow.build_state(participant, token, config)

    items = participant.get("scenario_items_snapshot") or json.dumps(
        SCENARIO_ITEMS
    )
    if isinstance(items, str):
        items = json.loads(items)
    item = next(
        (item for item in items if item["id"] == body.scenario_id), None
    )
    if item is None or not 0 <= body.selected_index < len(item["options"]):
        raise HTTPException(400, "Jawaban asesmen tidak valid")

    async with shared.pool.acquire() as conn:
        await conn.execute(
            """UPDATE participants
               SET scenario_answers = COALESCE(scenario_answers, '{}'::jsonb)
                   || $1::jsonb
               WHERE id = $2""",
            json.dumps({body.scenario_id: body.selected_index}),
            participant["id"],
        )
    return {"saved": True, "stage": "scenario", "remaining_seconds": remaining}


@router.post(
    "/exam/scenario/submit", dependencies=[Depends(shared.verify_seb)]
)
async def scenario_submit(body: SessionBody):
    participant, token = await workflow.get_session(
        body.participant_id, body.token
    )
    if participant["stage"] != "scenario":
        raise HTTPException(400, "Sesi asesmen skenario tidak aktif")
    items = participant.get("scenario_items_snapshot") or json.dumps(
        SCENARIO_ITEMS
    )
    answers = participant.get("scenario_answers") or "{}"
    if isinstance(items, str):
        items = json.loads(items)
    if isinstance(answers, str):
        answers = json.loads(answers)
    config = await shared.get_config()
    if (
        workflow.remaining_seconds(
            participant["scenario_started_at"],
            config["disc_duration_minutes"],
        )
        <= 0
    ):
        await workflow.do_complete(participant, auto=True)
        return await workflow.build_state(
            participant, token, config
        )
    unanswered = [
        item["id"] for item in items if item["id"] not in answers
    ]
    if unanswered:
        raise HTTPException(
            400,
            f"Masih ada {len(unanswered)} skenario yang belum dijawab",
        )
    await workflow.do_complete(participant)
    return await workflow.build_state(
        participant, token, config
    )


@router.post(
    "/exam/work-disc/answer", dependencies=[Depends(shared.verify_seb)]
)
async def work_disc_answer(body: WorkDiscAnswerBody):
    participant, _ = await workflow.get_session(
        body.participant_id, body.token
    )
    if participant["stage"] != "work_disc":
        raise HTTPException(400, "Sesi asesmen DISC tidak aktif")
    config = await shared.get_config()
    remaining = workflow.remaining_seconds(
        participant["work_disc_started_at"],
        config["work_disc_duration_minutes"],
    )
    if remaining <= 0:
        await workflow.do_complete(participant, auto=True, timed_out=True)
        return {"saved": False, "stage": "done", "remaining_seconds": 0}

    items = participant.get("work_disc_items_snapshot") or []
    if isinstance(items, str):
        items = json.loads(items)
    item = next((item for item in items if item["id"] == body.item_id), None)
    if item is None or not 0 <= body.selected_index < len(item["options"]):
        raise HTTPException(400, "Jawaban asesmen DISC tidak valid")

    async with shared.pool.acquire() as conn:
        await conn.execute(
            """UPDATE participants
               SET work_disc_answers = COALESCE(work_disc_answers, '{}'::jsonb)
                   || jsonb_build_object($1::text, $2::int)
               WHERE id = $3""",
            body.item_id,
            body.selected_index,
            participant["id"],
        )
    return {
        "saved": True,
        "stage": "work_disc",
        "remaining_seconds": remaining,
    }


@router.post(
    "/exam/work-disc/submit", dependencies=[Depends(shared.verify_seb)]
)
async def work_disc_submit(body: SessionBody):
    participant, token = await workflow.get_session(
        body.participant_id, body.token
    )
    if participant["stage"] != "work_disc":
        raise HTTPException(400, "Sesi asesmen DISC tidak aktif")
    config = await shared.get_config()
    remaining = workflow.remaining_seconds(
        participant["work_disc_started_at"],
        config["work_disc_duration_minutes"],
    )
    if remaining <= 0:
        await workflow.do_complete(participant, auto=True, timed_out=True)
        return {"stage": "done", "auto_submitted": True}

    items = participant.get("work_disc_items_snapshot") or []
    answers = participant.get("work_disc_answers") or {}
    if isinstance(items, str):
        items = json.loads(items)
    if isinstance(answers, str):
        answers = json.loads(answers)
    unanswered = [item["id"] for item in items if item["id"] not in answers]
    if unanswered:
        raise HTTPException(
            400, f"Masih ada {len(unanswered)} pertanyaan DISC yang belum dijawab"
        )

    await workflow.do_complete(participant)
    return {"stage": "done", "auto_submitted": False}


@router.post("/exam/violation")
async def log_violation(body: ViolationBody):
    participant, _ = await workflow.get_session(
        body.participant_id, body.token
    )
    if participant["stage"] == "done":
        return {"logged": False, "stage": "done"}
    async with shared.pool.acquire() as conn:
        await conn.execute(
            """INSERT INTO violation_logs
               (id, participant_id, token_code, violation_type, detail,
                stage, timestamp)
               VALUES ($1, $2, $3, $4, $5, $6, $7)""",
            str(uuid.uuid4()),
            participant["id"],
            participant["token_code"],
            body.violation_type,
            body.detail,
            participant["stage"],
            shared.now_utc(),
        )
        count = await conn.fetchval(
            """SELECT COUNT(*) FROM violation_logs
               WHERE participant_id = $1 AND violation_type IN
               ('tab-switch', 'fullscreen-exit', 'camera-off',
                'face-missing', 'multiple-faces', 'face-mismatch')""",
            participant["id"],
        )
        config = await shared.get_config()
        if count >= config["violation_threshold"]:
            participant = dict(
                await conn.fetchrow(
                    "SELECT * FROM participants WHERE id = $1",
                    participant["id"],
                )
            )
            if participant["stage"] == "tkj":
                await workflow.do_submit_tkj(participant, auto=True)
                participant = dict(
                    await conn.fetchrow(
                        "SELECT * FROM participants WHERE id = $1",
                        participant["id"],
                    )
                )
            if participant["stage"] in ("disc", "scenario", "work_disc"):
                await workflow.do_complete(
                    participant, auto=True, force_complete=True
                )
            await shared.manager.broadcast(
                {
                    "type": "exam_violation",
                    "participant": participant["name"],
                    "detail": f"Dikeluarkan: {body.violation_type}",
                }
            )
            return {
                "logged": True,
                "count": count,
                "auto_submitted": True,
                "stage": "done",
            }
    await shared.manager.broadcast(
        {
            "type": "exam_violation",
            "participant": participant["name"],
            "detail": f"Peringatan {count}: {body.violation_type}",
        }
    )
    return {
        "logged": True,
        "count": count,
        "auto_submitted": False,
        "remaining_warnings": config["violation_threshold"] - count,
    }
