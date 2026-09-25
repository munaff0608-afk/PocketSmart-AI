from datetime import datetime, timedelta, timezone
import jwt
from passlib.context import CryptContext
from fastapi import Request, HTTPException, status
from .config import get_settings
from .database import get_user_by_id

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
ALGORITHM = "HS256"
COOKIE_NAME = "pocketsmart_token"

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(password: str, hashed: str) -> bool:
    return pwd_context.verify(password, hashed)

def create_token(user_id: int, expires_minutes: int = 60 * 24) -> str:
    settings = get_settings()
    payload = {
        "sub": str(user_id),
        "exp": datetime.now(timezone.utc) + timedelta(minutes=expires_minutes),
        "iat": datetime.now(timezone.utc),
    }
    return jwt.encode(payload, settings.secret_key, algorithm=ALGORITHM)

def get_current_user(request: Request):
    token = request.cookies.get(COOKIE_NAME)
    if not token:
        return None
    try:
        payload = jwt.decode(token, get_settings().secret_key, algorithms=[ALGORITHM])
        user_id = int(payload["sub"])
        return get_user_by_id(user_id)
    except (jwt.PyJWTError, ValueError, TypeError):
        return None

def require_user(request: Request):
    user = get_current_user(request)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Login required")
    return user
