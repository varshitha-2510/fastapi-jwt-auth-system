from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from app.dependencies import (
    get_db,
    get_current_user
)
from app.dependencies import require_role
from app.models.user import User
from app.models.session import UserSession
from app.models.otp import OTP

from app.schemas.user import (
    UserCreate,
    UserResponse,
    UserLogin
)

from app.schemas.auth import TokenResponse
from app.schemas.session import LogoutRequest
from app.schemas.token import RefreshTokenRequest
from app.schemas.logout_all import LogoutAllRequest
from app.schemas.session_response import SessionResponse
from app.schemas.otp import (
    VerifyOTPRequest,
    EmailRequest
)
from app.schemas.password import (
    ForgotPasswordRequest,
    ResetPasswordRequest
)

from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    verify_token
)

from app.core.otp import generate_otp
from app.core.email import send_otp_email
from app.core.limiter import limiter
from app.core.config import settings

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)

from fastapi.responses import RedirectResponse
from app.core.oauth import oauth
# REGISTER

@router.post("/register", response_model=UserResponse)
async def register_user(
    user: UserCreate,
    db: Session = Depends(get_db)
):
    existing_user = db.query(User).filter(
        User.email == user.email
    ).first()

    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Email already exists"
        )

    new_user = User(
    name=user.name,
    email=user.email,
    password_hash=hash_password(user.password),
    role="user"
)

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    otp_code = generate_otp()

    otp = OTP(
        user_id=new_user.id,
        otp_code=otp_code,
        purpose="email_verification",
        expires_at=datetime.utcnow() + timedelta(minutes=10)
    )

    db.add(otp)
    db.commit()

    await send_otp_email(new_user.email, otp_code)

    return new_user


# LOGIN

@router.post("/login", response_model=TokenResponse)
@limiter.limit("5/minute")
def login_user(
    request: Request,
    user_data: UserLogin,
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(
        User.email == user_data.email
    ).first()

    if not user:
        raise HTTPException(
            status_code=401,
            detail="Invalid credentials"
        )

    if not verify_password(user_data.password, user.password_hash):
        raise HTTPException(
            status_code=401,
            detail="Invalid credentials"
        )

    active_sessions = db.query(UserSession).filter(
        UserSession.user_id == user.id,
        UserSession.is_active == True
    ).count()

    if active_sessions >= settings.MAX_SESSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Maximum {settings.MAX_SESSIONS} sessions allowed"
        )

    access_token = create_access_token({"sub": str(user.id)})
    refresh_token = create_refresh_token({"sub": str(user.id)})

    session = UserSession(
        user_id=user.id,
        refresh_token=refresh_token,
        device_info="Swagger UI"
    )

    db.add(session)
    db.commit()

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer"
    )


# LOGOUT

@router.post("/logout")
def logout_user(
    data: LogoutRequest,
    db: Session = Depends(get_db)
):
    session = db.query(UserSession).filter(
        UserSession.refresh_token == data.refresh_token,
        UserSession.is_active == True
    ).first()

    if not session:
        raise HTTPException(
            status_code=404,
            detail="Session not found"
        )

    session.is_active = False
    db.commit()

    return {"message": "Logged out successfully"}


# REFRESH TOKEN

@router.post("/refresh")
def refresh_access_token(
    data: RefreshTokenRequest
):
    payload = verify_token(data.refresh_token)

    if payload.get("type") != "refresh":
        raise HTTPException(
            status_code=401,
            detail="Invalid refresh token"
        )

    access_token = create_access_token({"sub": payload.get("sub")})

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }


# LOGOUT ALL DEVICES

@router.post("/logout-all")
def logout_all_devices(
    data: LogoutAllRequest,
    db: Session = Depends(get_db)
):
    sessions = db.query(UserSession).filter(
        UserSession.user_id == data.user_id,
        UserSession.is_active == True
    ).all()

    for session in sessions:
        session.is_active = False

    db.commit()

    return {"message": "Logged out from all devices successfully"}


# VIEW ALL SESSIONS

@router.get("/sessions", response_model=list[SessionResponse])
def get_sessions(
    db: Session = Depends(get_db)
):
    return db.query(UserSession).all()


# LOGOUT SPECIFIC SESSION

@router.delete("/sessions/{session_id}")
def logout_specific_session(
    session_id: str,
    db: Session = Depends(get_db)
):
    session = db.query(UserSession).filter(
        UserSession.id == session_id
    ).first()

    if not session:
        raise HTTPException(
            status_code=404,
            detail="Session not found"
        )

    session.is_active = False
    db.commit()

    return {"message": "Session logged out successfully"}


# SEND OTP

@router.post("/send-otp")
@limiter.limit("3/15minute")
async def send_otp_route(
    request: Request,
    data: EmailRequest,
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(
        User.email == data.email
    ).first()

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )
    old_otps = db.query(OTP).filter(
    OTP.user_id == user.id,
    OTP.is_used == False
    ).all()

    for old_otp in old_otps:
        old_otp.is_used = True

    db.commit()

    otp_code = generate_otp()

    otp = OTP(
        user_id=user.id,
        otp_code=otp_code,
        purpose="email_verification",
        expires_at=datetime.utcnow() + timedelta(minutes=10)
    )

    db.add(otp)
    db.commit()

    await send_otp_email(user.email, otp_code)

    return {"message": "OTP sent successfully"}


# VERIFY OTP

@router.post("/verify-otp")
def verify_otp_route(
    data: VerifyOTPRequest,
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(
        User.email == data.email
    ).first()

    otp = db.query(OTP).filter(
        OTP.user_id == user.id,
        OTP.otp_code == data.otp,
        OTP.is_used == False
    ).first()

    if not otp:
        raise HTTPException(
            status_code=400,
            detail="Invalid OTP"
        )

    if otp.expires_at < datetime.utcnow():
        raise HTTPException(
            status_code=400,
            detail="OTP expired"
        )

    otp.is_used = True
    db.commit()

    return {"message": "OTP verified successfully"}


# RESEND OTP

@router.post("/resend-otp")
@limiter.limit("3/15minute")
async def resend_otp(
    request: Request,
    data: EmailRequest,
    db: Session = Depends(get_db)
):
    return await send_otp_route(request,data, db)


# FORGOT PASSWORD

@router.post("/forgot-password")
async def forgot_password(
    data: ForgotPasswordRequest,
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(
        User.email == data.email
    ).first()

    otp_code = generate_otp()

    otp = OTP(
        user_id=user.id,
        otp_code=otp_code,
        purpose="forgot_password",
        expires_at=datetime.utcnow() + timedelta(minutes=10)
    )

    db.add(otp)
    db.commit()

    await send_otp_email(user.email, otp_code)

    return {"message": "Password reset OTP sent"}


# RESET PASSWORD

@router.post("/reset-password")
def reset_password(
    data: ResetPasswordRequest,
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(
        User.email == data.email
    ).first()

    otp = db.query(OTP).filter(
        OTP.user_id == user.id,
        OTP.otp_code == data.otp,
        OTP.purpose == "forgot_password",
        OTP.is_used == False
    ).first()

    if not otp:
        raise HTTPException(
            status_code=400,
            detail="Invalid OTP"
        )

    user.password_hash = hash_password(data.new_password)
    otp.is_used = True
    db.commit()

    return {"message": "Password reset successfully"}


# VERIFY EMAIL

@router.post("/verify-email")
def verify_email(
    data: VerifyOTPRequest,
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(
        User.email == data.email
    ).first()

    otp = db.query(OTP).filter(
        OTP.user_id == user.id,
        OTP.otp_code == data.otp,
        OTP.purpose == "email_verification",
        OTP.is_used == False
    ).first()

    if not otp:
        raise HTTPException(
            status_code=400,
            detail="Invalid OTP"
        )

    user.is_verified = True
    otp.is_used = True
    db.commit()

    return {"message": "Email verified successfully"}

@router.get("/me")
def get_my_profile(
        current_user: User = Depends(get_current_user)
):

    return {
        "id": current_user.id,
        "name": current_user.name,
        "email": current_user.email,
        "is_verified": current_user.is_verified
    }

@router.get("/admin")
def admin_dashboard(
    current_user: User = Depends(
        require_role("admin")
    )
):

    return {
        "message": "Welcome Admin"
    }

@router.get("/google/login")
async def google_login(request: Request):

    redirect_uri = request.url_for("google_callback")

    return await oauth.google.authorize_redirect(
        request,
        redirect_uri
    )

@router.get("/google/callback")
async def google_callback(
        request: Request,
        db: Session = Depends(get_db)
):

    token = await oauth.google.authorize_access_token(request)

    user_info = token.get("userinfo")

    email = user_info["email"]
    name = user_info["name"]

    user = db.query(User).filter(
        User.email == email
    ).first()

    if not user:

        user = User(
            name=name,
            email=email,
            password_hash="GOOGLE_LOGIN_USER",
            is_verified=True
        )

        db.add(user)
        db.commit()
        db.refresh(user)

    access_token = create_access_token(
        {"sub": str(user.id)}
    )

    refresh_token = create_refresh_token(
        {"sub": str(user.id)}
    )

    return {
        "message": "Google login successful",
        "access_token": access_token,
        "refresh_token": refresh_token,
        "user": {
            "id": str(user.id),
            "name": user.name,
            "email": user.email
        }
    }