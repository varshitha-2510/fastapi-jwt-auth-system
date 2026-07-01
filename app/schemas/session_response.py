from pydantic import BaseModel
from datetime import datetime
from uuid import UUID


class SessionResponse(BaseModel):

    id: UUID

    refresh_token: str

    device_info: str

    is_active: bool

    created_at: datetime

    class Config:
        from_attributes = True