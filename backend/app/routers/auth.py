from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, Request

from app import runtime as shared
from app.core.security import verify_password
from app.schemas.auth import LoginBody


router = APIRouter()


@router.post("/auth/login")
async def login(body: LoginBody, request: Request):
    email = body.email.strip().lower()
    ip = request.client.host if request.client else "unknown"
    identifier = f"{ip}:{email}"

    async with shared.pool.acquire() as conn:
        attempt = await conn.fetchrow(
            "SELECT count, last_attempt FROM login_attempts WHERE identifier = $1",
            identifier,
        )
        if attempt and attempt["count"] >= 5:
            if shared.now_utc() - attempt["last_attempt"] < timedelta(minutes=15):
                raise HTTPException(
                    429,
                    "Terlalu banyak percobaan gagal. Coba lagi dalam 15 menit.",
                )
            await conn.execute(
                "DELETE FROM login_attempts WHERE identifier = $1", identifier
            )

        admin = await conn.fetchrow(
            "SELECT id, email, name, role, password_hash FROM admins WHERE email = $1",
            email,
        )
        if not admin or not verify_password(body.password, admin["password_hash"]):
            await conn.execute(
                """INSERT INTO login_attempts (identifier, count, last_attempt)
                   VALUES ($1, 1, $2)
                   ON CONFLICT (identifier) DO UPDATE
                   SET count = login_attempts.count + 1, last_attempt = $2""",
                identifier,
                shared.now_utc(),
            )
            raise HTTPException(401, "Email atau password salah")

        await conn.execute(
            "DELETE FROM login_attempts WHERE identifier = $1", identifier
        )
        return {
            "access_token": shared.create_access_token(admin["id"], email),
            "user": {
                "id": admin["id"],
                "email": email,
                "name": admin.get("name", "Admin"),
                "role": "admin",
            },
        }


@router.get("/auth/me")
async def me(admin: dict = Depends(shared.get_current_admin)):
    return admin
