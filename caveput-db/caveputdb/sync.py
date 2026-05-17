"""Zenput → local DB sync.

Replicates what ZenputAPI.swift does:
  POST /api/v1/users/login/   → session cookie
  GET  /api/v2/ingredients/ingredients/?limit=1000&include_non_expiring=true
  GET  /api/v2/ingredients/template_groups/
Then stores in local SQLite.
"""

import httpx
import json
import logging
from . import config, database

log = logging.getLogger("caveputdb.sync")

_HEADERS = {
    "Content-Type": "application/json",
    "Accept": "application/json",
    "User-Agent": "CavePutDB/1.0 (Home Assistant Add-on)",
}

_is_syncing = False

def is_syncing() -> bool:
    return _is_syncing

async def run_sync() -> dict:
    global _is_syncing
    if _is_syncing:
        return {"status": "already_running"}

    _is_syncing = True
    try:
        return await _do_sync()
    finally:
        _is_syncing = False

async def _do_sync() -> dict:
    if not config.ZENPUT_EMAIL or not config.ZENPUT_PASSWORD:
        msg = "Zenput credentials not configured"
        database.log_sync_error(msg)
        log.error(msg)
        return {"status": "error", "error": msg}

    log.info("Starting Zenput sync...")

    async with httpx.AsyncClient(
        base_url=config.ZENPUT_BASE,
        headers=_HEADERS,
        follow_redirects=True,
        timeout=60,
    ) as client:
        # 1. Login
        try:
            r = await client.post("/api/v1/users/login/", json={
                "email": config.ZENPUT_EMAIL,
                "password": config.ZENPUT_PASSWORD,
            })
            if r.status_code not in range(200, 400):
                msg = f"Zenput login failed: HTTP {r.status_code}"
                database.log_sync_error(msg)
                log.error(msg)
                return {"status": "error", "error": msg}
            log.info("Zenput login OK")
        except Exception as e:
            msg = f"Zenput login error: {e}"
            database.log_sync_error(msg)
            log.error(msg)
            return {"status": "error", "error": msg}

        # 2. Fetch ingredients
        try:
            r = await client.get(
                "/api/v2/ingredients/ingredients/",
                params={"limit": 1000, "include_non_expiring": "true"},
            )
            r.raise_for_status()
            raw = r.json()
            ingredients = raw.get("data", raw) if isinstance(raw, dict) else raw
            # Filter disabled and non-label items (mirrors iOS app logic)
            ingredients = [
                i for i in ingredients
                if not i.get("is_disabled") and i.get("labels_support") is not False
            ]
            log.info(f"Fetched {len(ingredients)} ingredients")
        except Exception as e:
            msg = f"Ingredients fetch error: {e}"
            database.log_sync_error(msg)
            log.error(msg)
            return {"status": "error", "error": msg}

        # 3. Fetch template groups
        try:
            r = await client.get("/api/v2/ingredients/template_groups/")
            r.raise_for_status()
            raw = r.json()
            template_groups = raw.get("data", raw) if isinstance(raw, dict) else raw
            log.info(f"Fetched {len(template_groups)} template groups")
        except Exception as e:
            # Non-fatal — labels still work with fallback ZPL
            log.warning(f"Template groups fetch failed (non-fatal): {e}")
            template_groups = []

    # 4. Store
    database.save_catalog(ingredients, template_groups)
    log.info(f"Sync complete. {len(ingredients)} ingredients, {len(template_groups)} template groups saved.")
    return {"status": "ok", "ingredient_count": len(ingredients)}
