import hmac
from datetime import datetime, timedelta, timezone

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from . import config

_bearer = HTTPBearer()

def create_token(username: str) -> tuple[str, datetime]:
    expire = datetime.now(timezone.utc) + timedelta(days=config.JWT_EXPIRE_DAYS)
    payload = {"sub": username, "exp": expire}
    token = jwt.encode(payload, config.JWT_SECRET, algorithm=config.JWT_ALGORITHM)
    return token, expire

def decode_token(token: str) -> str:
    try:
        payload = jwt.decode(token, config.JWT_SECRET, algorithms=[config.JWT_ALGORITHM])
        username: str = payload.get("sub")
        if not username:
            raise ValueError("No subject")
        return username
    except jwt.PyJWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        ) from e

def require_auth(credentials: HTTPAuthorizationCredentials = Depends(_bearer)) -> str:
    return decode_token(credentials.credentials)

def check_credentials(username: str, password: str) -> bool:
    ok_user = hmac.compare_digest(username, config.DB_USERNAME)
    ok_pass = hmac.compare_digest(password, config.DB_PASSWORD)
    return ok_user and ok_pass
