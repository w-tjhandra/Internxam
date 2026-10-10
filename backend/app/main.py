"""ASGI application factory and centralized router registration."""

import os

from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from app.routers import admin, auth, exam, results
from app.runtime import lifespan, websocket_live


app = FastAPI(lifespan=lifespan)

app.include_router(auth.router, prefix="/api")
app.include_router(admin.router, prefix="/api")
app.include_router(results.router, prefix="/api")
app.include_router(exam.router, prefix="/api")
app.add_api_websocket_route("/api/admin/ws/live", websocket_live)

cors_origins = os.environ.get("CORS_ORIGINS", "*").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins if cors_origins != ["*"] else [],
    allow_origin_regex=".*" if cors_origins == ["*"] else None,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

__all__ = ["app"]
