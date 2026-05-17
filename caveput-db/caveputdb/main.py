import logging
import asyncio
from contextlib import asynccontextmanager
from datetime import datetime, timezone

from fastapi import APIRouter, FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from . import config, database, auth, sync

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
log = logging.getLogger("caveputdb")

# ── Scheduler ────────────────────────────────────────────────────────────────

_scheduler = AsyncIOScheduler()

@asynccontextmanager
async def lifespan(app: FastAPI):
    database.init_db()
    log.info(f"DB ready at {config.DB_PATH}")

    # Schedule weekly Zenput sync
    _scheduler.add_job(
        sync.run_sync,
        CronTrigger(day_of_week=config.SYNC_DOW, hour=config.SYNC_HOUR, minute=0),
        id="weekly_sync",
        replace_existing=True,
        misfire_grace_time=3600,
    )
    _scheduler.start()
    log.info(f"Sync scheduled: every {config.SYNC_DOW} at {config.SYNC_HOUR}:00")

    yield

    _scheduler.shutdown(wait=False)

# ── App ───────────────────────────────────────────────────────────────────────

app = FastAPI(title="CavePut DB", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

router = APIRouter(prefix="/caveput")

# ── Auth ──────────────────────────────────────────────────────────────────────

class LoginRequest(BaseModel):
    username: str
    password: str

class LoginResponse(BaseModel):
    token: str
    expires_at: str
    username: str

@router.post("/auth/login", response_model=LoginResponse)
async def login(body: LoginRequest):
    if not auth.check_credentials(body.username, body.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
        )
    token, expire = auth.create_token(body.username)
    return LoginResponse(
        token=token,
        expires_at=expire.isoformat(),
        username=body.username,
    )

# ── Catalog ───────────────────────────────────────────────────────────────────

@router.get("/api/v1/catalog")
async def get_catalog(username: str = Depends(auth.require_auth)):
    catalog = database.get_catalog()
    if catalog is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="No data yet. Trigger a sync first.",
        )
    return {
        "version": "1",
        "synced_at": catalog["synced_at"],
        "ingredients": catalog["ingredients"],
        "template_groups": catalog["template_groups"],
    }

# ── Status ────────────────────────────────────────────────────────────────────

@router.get("/api/v1/status")
async def get_status(username: str = Depends(auth.require_auth)):
    status_data = database.get_sync_status()
    next_run = _scheduler.get_job("weekly_sync")
    return {
        **status_data,
        "syncing": sync.is_syncing(),
        "next_sync": next_run.next_run_time.isoformat() if next_run and next_run.next_run_time else None,
    }

# ── Manual Sync ───────────────────────────────────────────────────────────────

@router.post("/api/v1/sync")
async def trigger_sync(username: str = Depends(auth.require_auth)):
    if sync.is_syncing():
        return {"status": "already_running"}
    asyncio.create_task(sync.run_sync())
    return {"status": "started"}

# ── Health (no auth) ──────────────────────────────────────────────────────────

@router.get("/health")
async def health():
    return {"status": "ok", "time": datetime.now(timezone.utc).isoformat()}

app.include_router(router)

# ── Entry Point ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "caveputdb.main:app",
        host="0.0.0.0",
        port=8765,
        log_level="info",
    )
