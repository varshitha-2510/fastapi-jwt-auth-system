# FastAPI JWT Authentication System

A production-ready Authentication and Authorization system built using **FastAPI** and **PostgreSQL**. This project implements secure user authentication with JWT, OTP-based email verification, session management, role-based access control, rate limiting, and Google SSO.

---

## 🚀 Features

* User Registration
* User Login
* JWT Access Token Authentication
* Refresh Token Support
* Secure Password Hashing using bcrypt
* Email Verification using OTP
* Resend OTP
* Forgot Password
* Reset Password
* OTP Expiration
* OTP Rate Limiting
* Session Management
* Maximum Active Session Limit
* Logout from Current Device
* Logout from All Devices
* Logout Specific Session
* Protected Routes
* Role-Based Access Control (RBAC)
* Rate Limiting using SlowAPI
* Google Single Sign-On (SSO)
* User Profile API

---

## 🛠️ Tech Stack

### Backend

* FastAPI
* Python

### Database

* PostgreSQL

### ORM

* SQLAlchemy

### Authentication & Security

* JWT (JSON Web Tokens)
* Passlib
* bcrypt
* OAuth2
* Google OAuth

### Email Services

* FastAPI-Mail

### Validation

* Pydantic

### Rate Limiting

* SlowAPI

### Server

* Uvicorn

---

## 📂 Project Structure

```bash
app/
│
├── core/
│   ├── config.py
│   ├── security.py
│   ├── email.py
│   ├── otp.py
│   ├── limiter.py
│   └── oauth.py
│
├── models/
│   ├── user.py
│   ├── otp.py
│   └── session.py
│
├── routers/
│   ├── auth.py
│   └── profile.py
│
├── schemas/
│
├── database.py
├── dependencies.py
└── main.py
```

---

## 🔐 Authentication Flow

### Registration Flow

```text
User Registration
       ↓
Generate OTP
       ↓
Send OTP via Email
       ↓
Verify Email
       ↓
Account Activated
```

### Login Flow

```text
User Login
      ↓
Verify Credentials
      ↓
Generate Access Token
      ↓
Generate Refresh Token
      ↓
Create User Session
```

---

## 📌 Implemented APIs

### Authentication APIs

| Method | Endpoint         |
| ------ | ---------------- |
| POST   | /auth/register   |
| POST   | /auth/login      |
| POST   | /auth/logout     |
| POST   | /auth/refresh    |
| POST   | /auth/logout-all |

### OTP APIs

| Method | Endpoint           |
| ------ | ------------------ |
| POST   | /auth/send-otp     |
| POST   | /auth/resend-otp   |
| POST   | /auth/verify-otp   |
| POST   | /auth/verify-email |

### Password APIs

| Method | Endpoint              |
| ------ | --------------------- |
| POST   | /auth/forgot-password |
| POST   | /auth/reset-password  |

### Session APIs

| Method | Endpoint                    |
| ------ | --------------------------- |
| GET    | /auth/sessions              |
| DELETE | /auth/sessions/{session_id} |

### Profile APIs

| Method | Endpoint |
| ------ | -------- |
| GET    | /auth/me |

### Admin APIs

| Method | Endpoint    |
| ------ | ----------- |
| GET    | /auth/admin |

### Google SSO APIs

| Method | Endpoint              |
| ------ | --------------------- |
| GET    | /auth/google/login    |
| GET    | /auth/google/callback |

---

## ⚙️ Installation

### Clone Repository

```bash
git clone https://github.com/your-username/fastapi-jwt-auth-system.git
```

### Navigate to Project

```bash
cd fastapi-jwt-auth-system
```

### Create Virtual Environment

```bash
python -m venv venv
```

### Activate Virtual Environment

#### Windows

```bash
venv\Scripts\activate
```

#### Linux/Mac

```bash
source venv/bin/activate
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Configure Environment Variables

Create a `.env` file and add:

```env
DATABASE_URL=
SECRET_KEY=
ALGORITHM=HS256

ACCESS_TOKEN_EXPIRE_MINUTES=60
REFRESH_TOKEN_EXPIRE_DAYS=30

MAX_SESSIONS=5

MAIL_USERNAME=
MAIL_PASSWORD=
MAIL_FROM=
MAIL_PORT=587
MAIL_SERVER=smtp.gmail.com
MAIL_STARTTLS=True
MAIL_SSL_TLS=False

GOOGLE_CLIENT_ID=
GOOGLE_CLIENT_SECRET=
```

---

## ▶️ Run the Application

```bash
uvicorn app.main:app --reload
```

Application runs on:

```text
http://127.0.0.1:8000
```

Swagger Documentation:

```text
http://127.0.0.1:8000/docs
```

---

## 🔒 Security Features

* Password Hashing
* JWT Authentication
* Refresh Tokens
* OTP Expiration
* Session Management
* Session Limiting
* Protected Routes
* Role-Based Access Control
* Rate Limiting
* Google OAuth Authentication

---

## 🔮 Future Enhancements

* JWT Token Blacklisting
* Soft Delete Users
* Login History
* Two Factor Authentication (2FA)
* GitHub SSO
* Refresh Token Rotation
* Audit Logs
