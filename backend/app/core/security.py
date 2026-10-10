from datetime import datetime, timedelta, timezone

import bcrypt
import jwt


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def verify_password(plain: str, hashed: str) -> bool:
    return bcrypt.checkpw(plain.encode(), hashed.encode())


def create_access_token(admin_id: str, email: str, secret: str, algorithm: str) -> str:
    return jwt.encode(
        {
            "sub": admin_id,
            "email": email,
            "type": "access",
            "exp": datetime.now(timezone.utc) + timedelta(hours=12),
        },
        secret,
        algorithm=algorithm,
    )
