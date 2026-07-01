from pydantic import BaseModel


class LogoutAllRequest(BaseModel):
    user_id: str