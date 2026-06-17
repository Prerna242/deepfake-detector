from datetime import datetime, timedelta, timezone

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.config import settings
from app.db.mongo import get_database
from app.models.user import UserCreate


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    password = password.strip()[:72]
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES,
    )
    to_encode.update({"exp": expire})

    return jwt.encode(
        to_encode,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM,
    )


def decode_token(token: str) -> dict:
    try:
        return jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
        )
    except JWTError as exc:
        raise ValueError("Invalid or expired token") from exc


async def register_user(user_data: UserCreate) -> dict:
    db = get_database()
    users_collection = db["users"]

    existing = await users_collection.find_one({"email": user_data.email})
    if existing:
        raise ValueError("An account with this email already exists.")

    new_user = {
        "username": user_data.username,
        "email": user_data.email,
        "password_hash": hash_password(user_data.password),
        "created_at": datetime.now(timezone.utc),
    }

    result = await users_collection.insert_one(new_user)

    return {
        "id": str(result.inserted_id),
        "username": new_user["username"],
        "email": new_user["email"],
        "created_at": new_user["created_at"],
    }


async def login_user(email: str, password: str) -> dict:
    db = get_database()
    user = await db["users"].find_one({"email": email})

    if not user or not verify_password(password, user["password_hash"]):
        raise ValueError("Invalid email or password.")

    token = create_access_token({"sub": str(user["_id"])})

    return {
        "access_token": token,
        "token_type": "bearer",
        "username": user["username"],
    }
