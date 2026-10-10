import copy
import json
import random

from fastapi import HTTPException

from app import runtime
from app.seed_data import (
    DISC_INTERPRETATIONS,
    SCENARIO_ASSESSMENT_VERSION,
    SCENARIO_ITEMS,
)
from app.services.scenario_assessment import compute_scenario_result
from app.services.work_disc import (
    WORK_DISC_VERSION,
    build_work_disc_items,
    score_work_disc,
)


async def get_session(participant_id: str, token_code: str) -> tuple:
    async with runtime.pool.acquire() as conn:
        participant = await conn.fetchrow(
            "SELECT * FROM participants WHERE id = $1", participant_id
        )
        if (
            not participant
            or participant["token_code"] != token_code.upper()
        ):
            raise HTTPException(404, "Sesi tidak ditemukan")
        token = await conn.fetchrow(
            "SELECT * FROM tokens WHERE code = $1", token_code.upper()
        )
        if not token:
            raise HTTPException(404, "Token tidak ditemukan")
        if token["status"] in ("completed", "expired", "revoked"):
            raise HTTPException(403, "Token sudah tidak berlaku")
        return dict(participant), dict(token)


def remaining_seconds(started_at, duration_minutes: int) -> int:
    if not started_at:
        return 0
    elapsed = (runtime.now_utc() - runtime.parse_dt(started_at)).total_seconds()
    return max(0, int(duration_minutes * 60 - elapsed))


async def tkj_questions_for(participant: dict) -> list:
    async with runtime.pool.acquire() as conn:
        order = json.loads(participant.get("question_order") or "[]")
        question_ids = [item["qid"] for item in order]
        if not question_ids:
            return []
        question_docs = await conn.fetch(
            """SELECT id, text, category, options FROM questions
               WHERE id = ANY($1::varchar[])""",
            question_ids,
        )
        question_map = {
            question["id"]: dict(
                question, options=json.loads(question["options"])
            )
            for question in question_docs
        }
        result = []
        for item in order:
            question = question_map.get(item["qid"])
            if question:
                result.append(
                    {
                        "id": question["id"],
                        "text": question["text"],
                        "category": question.get("category", ""),
                        "options": [
                            question["options"][index]
                            for index in item["option_order"]
                        ],
                    }
                )
        return result


def display_answers(participant: dict) -> dict:
    order = json.loads(participant.get("question_order") or "[]")
    option_orders = {
        item["qid"]: item["option_order"] for item in order
    }
    answers = json.loads(participant.get("tkj_answers") or "{}")
    result = {}
    for question_id, original_index in answers.items():
        option_order = option_orders.get(question_id)
        if option_order is not None and original_index in option_order:
            result[question_id] = option_order.index(original_index)
    return result


async def score_tkj(participant: dict) -> int:
    async with runtime.pool.acquire() as conn:
        order = json.loads(participant.get("question_order") or "[]")
        question_ids = [item["qid"] for item in order]
        if not question_ids:
            return 0
        question_docs = await conn.fetch(
            """SELECT id, correct_index FROM questions
               WHERE id = ANY($1::varchar[])""",
            question_ids,
        )
        correct_answers = {
            question["id"]: question["correct_index"]
            for question in question_docs
        }
        answers = json.loads(participant.get("tkj_answers") or "{}")
        return sum(
            1
            for question_id, answer in answers.items()
            if correct_answers.get(question_id) == answer
        )


async def do_submit_tkj(participant: dict, auto: bool = False) -> dict:
    score = await score_tkj(participant)
    order = json.loads(participant.get("question_order") or "[]")
    started_at = runtime.now_utc()
    scenario_snapshot = copy.deepcopy(SCENARIO_ITEMS)
    random.shuffle(scenario_snapshot)
    for item in scenario_snapshot:
        random.shuffle(item["options"])
    update = {
        "tkj_score": score,
        "tkj_total": len(order),
        "tkj_submitted_at": started_at,
        "stage": "scenario",
        "scenario_started_at": started_at,
        "scenario_items_snapshot": json.dumps(scenario_snapshot),
        "scenario_version": SCENARIO_ASSESSMENT_VERSION,
        "auto_submitted": bool(participant.get("auto_submitted")) or auto,
    }
    async with runtime.pool.acquire() as conn:
        await conn.execute(
            """UPDATE participants
               SET tkj_score=$1, tkj_total=$2, tkj_submitted_at=$3, stage=$4,
                   scenario_started_at=$5, scenario_items_snapshot=$6,
                   scenario_version=$7, auto_submitted=$8
               WHERE id=$9""",
            update["tkj_score"],
            update["tkj_total"],
            update["tkj_submitted_at"],
            update["stage"],
            update["scenario_started_at"],
            update["scenario_items_snapshot"],
            update["scenario_version"],
            update["auto_submitted"],
            participant["id"],
        )
    return update


async def compute_scenario(participant: dict) -> dict:
    items = participant.get("scenario_items_snapshot") or json.dumps(
        SCENARIO_ITEMS
    )
    answers = participant.get("scenario_answers") or "{}"
    if isinstance(items, str):
        items = json.loads(items)
    if isinstance(answers, str):
        answers = json.loads(answers)
    return compute_scenario_result(
        items,
        answers,
        participant.get("scenario_version") or SCENARIO_ASSESSMENT_VERSION,
    )


async def compute_disc(participant: dict) -> dict:
    async with runtime.pool.acquire() as conn:
        items = await conn.fetch(
            "SELECT * FROM disc_items ORDER BY group_index ASC"
        )
    most = {"D": 0, "I": 0, "S": 0, "C": 0}
    least = {"D": 0, "I": 0, "S": 0, "C": 0}
    answers = json.loads(participant.get("disc_answers") or "{}")
    for item in items:
        statements = json.loads(item["statements"])
        answer = answers.get(str(item["group_index"]))
        if not answer:
            continue
        if 0 <= answer["most"] < len(statements):
            most[statements[answer["most"]]["dimension"]] += 1
        if 0 <= answer["least"] < len(statements):
            least[statements[answer["least"]]["dimension"]] += 1
    change = {
        dimension: most[dimension] - least[dimension]
        for dimension in "DISC"
    }
    dominant = max(change, key=lambda dimension: change[dimension])
    return {
        "most": most,
        "least": least,
        "change": change,
        "dominant": dominant,
        "interpretation": DISC_INTERPRETATIONS.get(dominant, ""),
        "answered_groups": len(answers),
        "total_groups": len(items),
    }


async def do_complete(
    participant: dict,
    auto: bool = False,
    force_complete: bool = False,
    timed_out: bool = False,
) -> dict:
    stage = participant.get("stage")
    work_disc_skipped = False
    if stage == "scenario":
        scenario_result = await compute_scenario(participant)
        config = await runtime.get_config()
        if config["work_disc_enabled"] and not force_complete:
            started_at = runtime.now_utc()
            items = build_work_disc_items()
            random.shuffle(items)
            for item in items:
                random.shuffle(item["options"])
            snapshot = json.dumps(items)
            async with runtime.pool.acquire() as conn:
                await conn.execute(
                    """UPDATE participants SET scenario_result=$1, stage='work_disc',
                       work_disc_started_at=$2, work_disc_items_snapshot=$3,
                       work_disc_version=$4, auto_submitted=$5 WHERE id=$6""",
                    json.dumps(scenario_result),
                    started_at,
                    snapshot,
                    WORK_DISC_VERSION,
                    bool(participant.get("auto_submitted")) or auto,
                    participant["id"],
                )
            await runtime.manager.broadcast(
                {
                    "type": "exam_stage",
                    "participant": participant["name"],
                    "detail": "memulai asesmen situasi kerja DISC",
                }
            )
            return {
                "scenario_result": json.dumps(scenario_result),
                "stage": "work_disc",
                "work_disc_started_at": started_at,
                "work_disc_items_snapshot": snapshot,
            }
        work_disc_skipped = not force_complete
        result_column = "scenario_result"
        result = scenario_result
        completion_label = "asesmen skenario PKL"
    elif stage == "work_disc":
        snapshot = participant.get("work_disc_items_snapshot") or "[]"
        answers = participant.get("work_disc_answers") or "{}"
        if isinstance(snapshot, str):
            snapshot = json.loads(snapshot)
        if isinstance(answers, str):
            answers = json.loads(answers)
        result = score_work_disc(
            snapshot, answers, auto_submitted=timed_out
        )
        result_column = "work_disc_result"
        completion_label = "asesmen situasi kerja DISC"
    else:
        result = await compute_disc(participant)
        result_column = "disc_result"
        completion_label = "Psikotes DISC historis"
    update = {
        result_column: json.dumps(result),
        "stage": "done",
        "completed_at": runtime.now_utc(),
        "auto_submitted": bool(participant.get("auto_submitted")) or auto,
    }
    async with runtime.pool.acquire() as conn:
        await conn.execute(
            f"""UPDATE participants SET {result_column}=$1, stage=$2,
                completed_at=$3, auto_submitted=$4,
                work_disc_auto_submitted=CASE WHEN $6 = 'work_disc' THEN $7
                    ELSE work_disc_auto_submitted END,
                work_disc_skipped=CASE WHEN $8 THEN TRUE
                    ELSE work_disc_skipped END
                WHERE id=$5""",
            update[result_column],
            update["stage"],
            update["completed_at"],
            update["auto_submitted"],
            participant["id"],
            stage,
            timed_out,
            work_disc_skipped,
        )
        token = await conn.fetchrow(
            "SELECT type FROM tokens WHERE code=$1",
            participant["token_code"],
        )
        if token and token["type"] != "group":
            await conn.execute(
                """UPDATE tokens SET status='completed', completed_at=$1
                   WHERE code=$2""",
                update["completed_at"],
                participant["token_code"],
            )
    await runtime.manager.broadcast(
        {
            "type": "exam_complete",
            "participant": participant["name"],
            "detail": f"menyelesaikan {completion_label}",
        }
    )
    return update


async def build_state(participant: dict, token: dict, config: dict) -> dict:
    async with runtime.pool.acquire() as conn:
        participant = dict(
            await conn.fetchrow(
                "SELECT * FROM participants WHERE id = $1",
                participant["id"],
            )
        )
        violation_count = await conn.fetchval(
            "SELECT COUNT(*) FROM violation_logs WHERE participant_id = $1",
            participant["id"],
        )
    state = {
        "participant_id": participant["id"],
        "name": participant["name"],
        "stage": participant["stage"],
        "violation_count": violation_count,
        "violation_threshold": config["violation_threshold"],
    }
    if participant["stage"] == "tkj":
        remaining = remaining_seconds(
            participant["tkj_started_at"], config["tkj_duration_minutes"]
        )
        if remaining <= 0:
            await do_submit_tkj(participant, auto=False)
            return await build_state(participant, token, config)
        state.update(
            {
                "questions": await tkj_questions_for(participant),
                "answers": display_answers(participant),
                "remaining_seconds": remaining,
            }
        )
    elif participant["stage"] == "disc":
        remaining = remaining_seconds(
            participant["disc_started_at"], config["disc_duration_minutes"]
        )
        if remaining <= 0:
            await do_complete(participant, auto=False)
            return await build_state(participant, token, config)
        async with runtime.pool.acquire() as conn:
            items = await conn.fetch(
                "SELECT * FROM disc_items ORDER BY group_index ASC"
            )
        state.update(
            {
                "disc_items": [
                    {
                        "group_index": item["group_index"],
                        "statements": [
                            statement["text"]
                            for statement in json.loads(item["statements"])
                        ],
                    }
                    for item in items
                ],
                "disc_answers": json.loads(
                    participant.get("disc_answers") or "{}"
                ),
                "remaining_seconds": remaining,
            }
        )
    elif participant["stage"] == "scenario":
        remaining = remaining_seconds(
            participant["scenario_started_at"],
            config["disc_duration_minutes"],
        )
        if remaining <= 0:
            await do_complete(participant, auto=True)
            return await build_state(participant, token, config)
        items = participant.get("scenario_items_snapshot") or json.dumps(
            SCENARIO_ITEMS
        )
        answers = participant.get("scenario_answers") or "{}"
        if isinstance(items, str):
            items = json.loads(items)
        if isinstance(answers, str):
            answers = json.loads(answers)
        state.update(
            {
                "scenario_version": participant.get("scenario_version")
                or SCENARIO_ASSESSMENT_VERSION,
                "scenario_items": [
                    {
                        "id": item["id"],
                        "situation": item["situation"],
                        "options": [
                            option["text"] for option in item["options"]
                        ],
                    }
                    for item in items
                ],
                "scenario_answers": answers,
                "remaining_seconds": remaining,
            }
        )
    elif participant["stage"] == "work_disc":
        remaining = remaining_seconds(
            participant["work_disc_started_at"],
            config["work_disc_duration_minutes"],
        )
        if remaining <= 0:
            await do_complete(participant, auto=True, timed_out=True)
            return await build_state(participant, token, config)
        items = participant.get("work_disc_items_snapshot") or "[]"
        answers = participant.get("work_disc_answers") or "{}"
        if isinstance(items, str):
            items = json.loads(items)
        if isinstance(answers, str):
            answers = json.loads(answers)
        state.update(
            {
                "work_disc_items": [
                    {
                        "id": item["id"],
                        "situation": item["situation"],
                        "options": [
                            option["text"] for option in item["options"]
                        ],
                    }
                    for item in items
                ],
                "work_disc_answers": answers,
                "remaining_seconds": remaining,
            }
        )
    return state
