import os

ZENPUT_BASE = "https://www.zenput.com"
ZENPUT_EMAIL = os.environ.get("CAVEPUT_ZENPUT_EMAIL", "")
ZENPUT_PASSWORD = os.environ.get("CAVEPUT_ZENPUT_PASSWORD", "")

DB_USERNAME = os.environ.get("CAVEPUT_DB_USERNAME", "caveput")
DB_PASSWORD = os.environ.get("CAVEPUT_DB_PASSWORD", "changeme")

SYNC_HOUR = int(os.environ.get("CAVEPUT_SYNC_HOUR", "23"))
SYNC_DOW = os.environ.get("CAVEPUT_SYNC_DOW", "sun")

DATA_DIR = os.environ.get("CAVEPUT_DATA_DIR", "/data")
DB_PATH = os.path.join(DATA_DIR, "caveput.db")

# JWT
JWT_SECRET = os.environ.get("CAVEPUT_JWT_SECRET", DB_PASSWORD + "_jwt_secret_caveput")
JWT_ALGORITHM = "HS256"
JWT_EXPIRE_DAYS = 30
