import json
import uuid
from datetime import datetime, timezone

from app.core.security import hash_password, verify_password
from app.seed_data import TKJ_QUESTIONS, build_disc_items


async def initialize_schema(pool) -> None:
    async with pool.acquire() as conn:
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS admins (
                id VARCHAR(36) PRIMARY KEY, email VARCHAR(255) UNIQUE NOT NULL, name VARCHAR(255),
                role VARCHAR(50), password_hash VARCHAR(255), created_at TIMESTAMP WITH TIME ZONE
            );
            CREATE TABLE IF NOT EXISTS exam_configs (
                id VARCHAR(50) PRIMARY KEY, tkj_duration_minutes INT, disc_duration_minutes INT,
                tkj_question_count INT, violation_threshold INT, require_seb BOOLEAN, seb_browser_exam_key VARCHAR(255),
                work_disc_enabled BOOLEAN NOT NULL DEFAULT TRUE,
                work_disc_duration_minutes INT NOT NULL DEFAULT 60
            );
            ALTER TABLE exam_configs ADD COLUMN IF NOT EXISTS work_disc_enabled BOOLEAN NOT NULL DEFAULT TRUE;
            ALTER TABLE exam_configs ADD COLUMN IF NOT EXISTS work_disc_duration_minutes INT NOT NULL DEFAULT 60;
            CREATE TABLE IF NOT EXISTS login_attempts (
                identifier VARCHAR(255) PRIMARY KEY, count INT, last_attempt TIMESTAMP WITH TIME ZONE
            );
            CREATE TABLE IF NOT EXISTS tokens (
                id VARCHAR(36) PRIMARY KEY, code VARCHAR(50) UNIQUE NOT NULL, status VARCHAR(50),
                created_at TIMESTAMP WITH TIME ZONE, participant_id VARCHAR(36),
                activated_at TIMESTAMP WITH TIME ZONE, completed_at TIMESTAMP WITH TIME ZONE
            );
            ALTER TABLE tokens ADD COLUMN IF NOT EXISTS type VARCHAR(20) DEFAULT 'single';
            ALTER TABLE tokens ADD COLUMN IF NOT EXISTS max_uses INT DEFAULT 1;
            ALTER TABLE tokens ADD COLUMN IF NOT EXISTS usage_count INT DEFAULT 0;
            CREATE TABLE IF NOT EXISTS questions (
                id VARCHAR(36) PRIMARY KEY, text TEXT, options JSONB, correct_index INT,
                category VARCHAR(100), difficulty VARCHAR(50), created_at TIMESTAMP WITH TIME ZONE
            );
            CREATE TABLE IF NOT EXISTS disc_items (
                group_index INT PRIMARY KEY, statements JSONB
            );
            CREATE TABLE IF NOT EXISTS participants (
                id VARCHAR(36) PRIMARY KEY, name VARCHAR(255), school VARCHAR(255), class_name VARCHAR(255),
                token_code VARCHAR(50), stage VARCHAR(50), question_order JSONB, tkj_answers JSONB,
                tkj_score INT, tkj_total INT, tkj_started_at TIMESTAMP WITH TIME ZONE, tkj_submitted_at TIMESTAMP WITH TIME ZONE,
                disc_answers JSONB, disc_started_at TIMESTAMP WITH TIME ZONE, disc_result JSONB,
                scenario_answers JSONB DEFAULT '{}'::jsonb, scenario_started_at TIMESTAMP WITH TIME ZONE,
                scenario_result JSONB, scenario_items_snapshot JSONB, scenario_version VARCHAR(100),
                work_disc_answers JSONB DEFAULT '{}'::jsonb,
                work_disc_started_at TIMESTAMP WITH TIME ZONE,
                work_disc_result JSONB,
                work_disc_items_snapshot JSONB,
                work_disc_version VARCHAR(100),
                work_disc_auto_submitted BOOLEAN NOT NULL DEFAULT FALSE,
                work_disc_skipped BOOLEAN NOT NULL DEFAULT FALSE,
                auto_submitted BOOLEAN, created_at TIMESTAMP WITH TIME ZONE, completed_at TIMESTAMP WITH TIME ZONE
            );
            ALTER TABLE participants ADD COLUMN IF NOT EXISTS scenario_answers JSONB DEFAULT '{}'::jsonb;
            ALTER TABLE participants ADD COLUMN IF NOT EXISTS scenario_started_at TIMESTAMP WITH TIME ZONE;
            ALTER TABLE participants ADD COLUMN IF NOT EXISTS scenario_result JSONB;
            ALTER TABLE participants ADD COLUMN IF NOT EXISTS scenario_items_snapshot JSONB;
            ALTER TABLE participants ADD COLUMN IF NOT EXISTS scenario_version VARCHAR(100);
            ALTER TABLE participants ADD COLUMN IF NOT EXISTS work_disc_answers JSONB NOT NULL DEFAULT '{}'::jsonb;
            ALTER TABLE participants ADD COLUMN IF NOT EXISTS work_disc_started_at TIMESTAMP WITH TIME ZONE;
            ALTER TABLE participants ADD COLUMN IF NOT EXISTS work_disc_result JSONB;
            ALTER TABLE participants ADD COLUMN IF NOT EXISTS work_disc_items_snapshot JSONB;
            ALTER TABLE participants ADD COLUMN IF NOT EXISTS work_disc_version VARCHAR(100);
            ALTER TABLE participants ADD COLUMN IF NOT EXISTS work_disc_auto_submitted BOOLEAN NOT NULL DEFAULT FALSE;
            ALTER TABLE participants ADD COLUMN IF NOT EXISTS work_disc_skipped BOOLEAN NOT NULL DEFAULT FALSE;
            CREATE TABLE IF NOT EXISTS violation_logs (
                id VARCHAR(36) PRIMARY KEY, participant_id VARCHAR(36), token_code VARCHAR(50),
                violation_type VARCHAR(100), detail TEXT, stage VARCHAR(50), timestamp TIMESTAMP WITH TIME ZONE
            );
        """)


async def seed_initial_data(pool) -> None:
    async with pool.acquire() as conn:
        email = "admin@axelbit.com"
        password = "ax3lb1t"
        admin = await conn.fetchrow("SELECT id, password_hash FROM admins WHERE email = $1", email)
        if not admin:
            await conn.execute(
                "INSERT INTO admins (id, email, name, role, password_hash, created_at) VALUES ($1, $2, $3, $4, $5, $6)",
                str(uuid.uuid4()), email, "Admin", "admin", hash_password(password), datetime.now(timezone.utc),
            )
        elif not verify_password(password, admin["password_hash"]):
            await conn.execute(
                "UPDATE admins SET password_hash = $1 WHERE email = $2",
                hash_password(password), email,
            )

        question_count = await conn.fetchval("SELECT COUNT(*) FROM questions")
        if question_count == 0:
            for question in TKJ_QUESTIONS:
                await conn.execute(
                    "INSERT INTO questions (id, text, options, correct_index, category, difficulty, created_at) VALUES ($1, $2, $3, $4, $5, $6, $7)",
                    str(uuid.uuid4()), question["text"], json.dumps(question["options"]),
                    question["correct_index"], question["category"], question["difficulty"],
                    datetime.now(timezone.utc),
                )

        disc_count = await conn.fetchval("SELECT COUNT(*) FROM disc_items")
        if disc_count == 0:
            for item in build_disc_items():
                await conn.execute(
                    "INSERT INTO disc_items (group_index, statements) VALUES ($1, $2)",
                    item["group_index"], json.dumps(item["statements"]),
                )
