import logging
from contextlib import asynccontextmanager

import spacy
import structlog
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from backend.api.routes import chat, ingest, progress, quiz
from backend.config.settings import settings

structlog.configure(
    processors=[
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.add_log_level,
        structlog.processors.JSONRenderer(),
    ],
    logger_factory=structlog.stdlib.LoggerFactory(),
)
logging.basicConfig(level=logging.INFO)

logger = structlog.get_logger()


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("loading_spacy_model")
    try:
        spacy.load("en_core_web_sm")
    except OSError:
        logger.warning("spacy_model_missing", hint="run: python -m spacy download en_core_web_sm")
    logger.info("startup_complete")
    yield
    logger.info("shutdown")


app = FastAPI(title="AI Tutor Agent API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error("unhandled_exception", path=str(request.url), error=str(exc))
    return JSONResponse(
        status_code=500,
        content={
            "type": "about:blank",
            "title": "Internal Server Error",
            "status": 500,
            "detail": str(exc),
            "instance": str(request.url),
        },
        media_type="application/problem+json",
    )


app.include_router(chat.router, prefix="/api")
app.include_router(ingest.router, prefix="/api")
app.include_router(quiz.router, prefix="/api")
app.include_router(progress.router, prefix="/api")


@app.get("/api/health")
async def health():
    return {"status": "ok"}
