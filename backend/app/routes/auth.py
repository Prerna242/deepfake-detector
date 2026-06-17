from fastapi import APIRouter, HTTPException, status

from app.models.user import TokenResponse, UserCreate, UserLogin, UserResponse
from app.services.auth_service import login_user, register_user


router = APIRouter(prefix="/api/auth", tags=["Authentication"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserCreate):
    try:
        return await register_user(user_data)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@router.post("/login", response_model=TokenResponse)
async def login(credentials: UserLogin):
    try:
        return await login_user(credentials.email, credentials.password)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc)) from exc
