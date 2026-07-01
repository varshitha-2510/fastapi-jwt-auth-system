from pydantic import BaseModel


class VerifyOTPRequest(BaseModel):
    email: str
    otp: str


class ResendOTPRequest(BaseModel):
    email: str


class EmailRequest(BaseModel):
    email: str