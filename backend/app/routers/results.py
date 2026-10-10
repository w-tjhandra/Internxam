import json

from fastapi import APIRouter, Depends, HTTPException

from app import runtime as shared
from app.seed_data import SCENARIO_INDICATORS


router = APIRouter()


async def participant_summary(participant: dict, conn) -> dict:
    violation_count = await conn.fetchval(
        "SELECT COUNT(*) FROM violation_logs WHERE participant_id = $1",
        participant["id"],
    )
    disc = json.loads(participant.get("disc_result") or "{}")
    scenario = json.loads(participant.get("scenario_result") or "{}")
    work_disc = json.loads(participant.get("work_disc_result") or "{}")
    if work_disc:
        work_disc_status = work_disc.get("status", "complete")
    elif participant.get("work_disc_skipped"):
        work_disc_status = "skipped"
    elif participant.get("stage") == "work_disc":
        work_disc_status = "in_progress"
    else:
        work_disc_status = "not_started"
    return {
        "id": participant["id"],
        "name": participant["name"],
        "school": participant["school"],
        "class_name": participant["class_name"],
        "token_code": participant["token_code"],
        "stage": participant["stage"],
        "tkj_score": participant.get("tkj_score"),
        "tkj_total": participant.get("tkj_total"),
        "disc_dominant": disc.get("dominant"),
        "violation_count": violation_count,
        "scenario_answered": scenario.get("answered_scenarios", 0),
        "scenario_total": scenario.get("total_scenarios", 0),
        "scenario_version": participant.get("scenario_version"),
        "work_disc_status": work_disc_status,
        "work_disc_answered": work_disc.get("answered_items", 0),
        "work_disc_total": work_disc.get("total_items", 30),
        "work_disc_auto_submitted": participant.get(
            "work_disc_auto_submitted", False
        ),
        "auto_submitted": participant.get("auto_submitted", False),
        "created_at": shared.iso(participant.get("created_at")),
        "completed_at": shared.iso(participant.get("completed_at")),
    }


@router.get("/admin/results")
async def list_results(admin: dict = Depends(shared.get_current_admin)):
    async with shared.pool.acquire() as conn:
        participants = await conn.fetch(
            "SELECT * FROM participants ORDER BY created_at DESC LIMIT 2000"
        )
        return [
            await participant_summary(dict(participant), conn)
            for participant in participants
        ]


@router.get("/admin/results/export")
async def export_results(
    format: str = "csv", admin: dict = Depends(shared.get_current_admin)
):
    async with shared.pool.acquire() as conn:
        participants = await conn.fetch(
            "SELECT * FROM participants ORDER BY created_at DESC LIMIT 5000"
        )
        headers = [
            "Nama",
            "Sekolah",
            "Kelas",
            "Token",
            "Status",
            "Skor TKJ",
            "Total Soal",
            "Persentase",
            *[
                f"Skenario: {indicator['label']} (rata-rata / 3)"
                for indicator in SCENARIO_INDICATORS
            ],
            "Versi Asesmen",
            "DISC D (historis)",
            "DISC I (historis)",
            "DISC S (historis)",
            "DISC C (historis)",
            "Profil DISC (historis)",
            "Status DISC",
            "DISC D (%)",
            "DISC I (%)",
            "DISC S (%)",
            "DISC C (%)",
            "Butir DISC terjawab",
            "DISC submit otomatis",
            "Pelanggaran",
            "Auto Submit",
            "Selesai",
        ]
        rows = []
        for participant in participants:
            participant = dict(participant)
            summary = await participant_summary(participant, conn)
            disc = json.loads(participant.get("disc_result") or "{}")
            work_disc = json.loads(
                participant.get("work_disc_result") or "{}"
            )
            scenario = json.loads(participant.get("scenario_result") or "{}")
            indicator_scores = scenario.get("indicators", {})
            percentage = (
                round(
                    100 * (summary["tkj_score"] or 0) / summary["tkj_total"],
                    1,
                )
                if summary.get("tkj_total")
                else ""
            )
            rows.append(
                [
                    summary["name"],
                    summary["school"],
                    summary["class_name"],
                    summary["token_code"],
                    summary["stage"],
                    summary["tkj_score"]
                    if summary["tkj_score"] is not None
                    else "",
                    summary["tkj_total"] or "",
                    percentage,
                    *[
                        indicator_scores.get(indicator["id"], {}).get(
                            "average", ""
                        )
                        for indicator in SCENARIO_INDICATORS
                    ],
                    summary["scenario_version"] or "",
                    *[
                        disc.get("change", {}).get(dimension, "")
                        for dimension in "DISC"
                    ],
                    summary["disc_dominant"] or "",
                    summary["work_disc_status"],
                    *[
                        work_disc.get("scores", {}).get(dimension, "")
                        for dimension in "DISC"
                    ],
                    summary["work_disc_answered"],
                    "Ya" if summary["work_disc_auto_submitted"] else "Tidak",
                    summary["violation_count"],
                    "Ya" if summary["auto_submitted"] else "Tidak",
                    summary["completed_at"] or "",
                ]
            )
        return shared.build_export(headers, rows, "hasil_ujian", format)


@router.get("/admin/results/{pid}")
async def result_detail(
    pid: str, admin: dict = Depends(shared.get_current_admin)
):
    async with shared.pool.acquire() as conn:
        participant = await conn.fetchrow(
            "SELECT * FROM participants WHERE id = $1", pid
        )
        if not participant:
            raise HTTPException(404, "Peserta tidak ditemukan")
        participant = dict(participant)
        violations = await conn.fetch(
            """SELECT * FROM violation_logs WHERE participant_id = $1
               ORDER BY timestamp ASC""",
            pid,
        )
        summary = await participant_summary(participant, conn)
        return {
            **summary,
            "disc_result": json.loads(participant.get("disc_result") or "{}"),
            "work_disc_result": json.loads(
                participant.get("work_disc_result") or "{}"
            ),
            "scenario_result": json.loads(
                participant.get("scenario_result") or "{}"
            ),
            "violations": [dict(violation) for violation in violations],
            "tkj_answers": json.loads(participant.get("tkj_answers") or "{}"),
            "tkj_started_at": shared.iso(participant.get("tkj_started_at")),
        }
