from fastapi import APIRouter
from app.core.auth import auth_manager

router = APIRouter()

@router.post("/token")
async def create_token(user_id: str):
    """Create authentication token."""
    access_token = auth_manager.create_access_token(data={"sub": user_id})
    return {"access_token": access_token, "token_type": "bearer"}