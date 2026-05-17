from datetime import datetime, timedelta, timezone
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from . import config

_pwd_ctx = CryptContext(schemes=["bcrypt"], deprecated="auto")
_bearer = HTTPBearer()

def verify_password(plain: str, hashed: str) -> bool:
    return _pwd_ctx.verify(plain, hashed)

def hash_password(plain: str) -> str:
    return _pwd_ctx.hash(plain)

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
    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        ) from e

def require_auth(credentials: HTTPAuthorizationCredentials = Depends(_bearer)) -> str:
    return decode_token(credentials.credentials)

def check_credentials(username: str, password: str) -> bool:
    return username == config.DB_USERNAME and password == config.DB_PASSWORD
