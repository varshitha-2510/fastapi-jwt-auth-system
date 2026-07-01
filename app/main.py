from fastapi import FastAPI

from slowapi.middleware import SlowAPIMiddleware
from app.core.limiter import limiter

from app.database import Base, engine

from app.routers import auth
from app.routers import profile

from app.models.otp import OTP

from starlette.middleware.sessions import SessionMiddleware
from app.core.config import settings


# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Authentication API"
)

# Add Session Middleware for Google SSO
app.add_middleware(
    SessionMiddleware,
    secret_key=settings.SECRET_KEY
)

# Rate Limiter
app.state.limiter = limiter

app.add_middleware(
    SlowAPIMiddleware
)

# Routers
app.include_router(auth.router)
app.include_router(profile.router)


@app.get("/")
def home():
    return {
        "message": "Authentication API Running Successfully"
    }