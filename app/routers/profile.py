from fastapi import APIRouter
from fastapi import Depends

from app.dependencies import get_current_user

from app.models.user import User

from app.schemas.user import UserResponse

router = APIRouter(
    prefix="/profile",
    tags=["Profile"]
)


@router.get(
    "/",
    response_model=UserResponse
)
def get_profile(
    current_user: User = Depends(get_current_user)
):

    return current_user