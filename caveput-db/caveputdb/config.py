import json
import os

# HA add-ons get their config at /data/options.json
_options: dict = {}
try:
    with open("/data/options.json") as f:
        _options = json.load(f)
except FileNotFoundError:
    pass  # running outside HA (dev / testing)

def _get(key: str, env_key: str, default: str = "") -> str:
    return str(_options.get(key) or os.environ.get(env_key) or default)

ZENPUT_BASE    = "https://www.zenput.com"
ZENPUT_EMAIL   = _get("zenput_email",    "CAVEPUT_ZENPUT_EMAIL")
ZENPUT_PASSWORD= _get("zenput_password", "CAVEPUT_ZENPUT_PASSWORD")

DB_USERNAME = _get("db_username",       "CAVEPUT_DB_USERNAME", "caveput")
DB_PASSWORD = _get("db_password",       "CAVEPUT_DB_PASSWORD", "changeme")

SYNC_HOUR = int(_get("sync_hour",           "CAVEPUT_SYNC_HOUR", "23"))
SYNC_DOW  = _get("sync_day_of_week",        "CAVEPUT_SYNC_DOW",  "sun")

DATA_DIR = "/data"
DB_PATH  = os.path.join(DATA_DIR, "caveput.db")

JWT_SECRET    = DB_PASSWORD + "_jwt_caveput"
JWT_ALGORITHM = "HS256"
JWT_EXPIRE_DAYS = 30
