# main.py
# Run with: uvicorn main:app --reload

import os
from datetime import datetime, timedelta, timezone
from typing import Annotated

from fastapi import FastAPI, Response, Depends, HTTPException, status, Cookie, Body
from fastapi.middleware.cors import CORSMiddleware
from jose import JWTError, jwt
from pydantic import BaseModel
from pydantic_settings import BaseSettings

# --- 1. Settings and Configuration ---
# Pydantic V2 will automatically load variables from a .env file
# Create a file named .env in the same directory with this content:
#
# SECRET_KEY="<your-super-secret-key>"
# ALGORITHM="HS256"
# ACCESS_TOKEN_EXPIRE_MINUTES=30
# REFRESH_TOKEN_EXPIRE_DAYS=7
#
# Generate a secret key with: openssl rand -hex 32


class Settings(BaseSettings):
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    class Config:
        env_file = ".env"
        # For case-insensitive environment variables
        case_sensitive = False


settings = Settings()


# --- 2. Pydantic Schemas (Data Models) ---
class TokenData(BaseModel):
    username: str | None = None


class User(BaseModel):
    username: str
    email: str | None = None
    full_name: str | None = None


# --- 3. Database Simulation ---
# In a real project, this would connect to your database.
fake_users_db = {
    "johndoe": {
        "username": "johndoe",
        "full_name": "John Doe",
        "email": "johndoe@example.com",
    }
}


def get_user(username: str):
    if username in fake_users_db:
        return User(**fake_users_db[username])
    return None


# --- 4. Security and Token Management ---
def create_access_token(data: dict):
    """Creates a short-lived Access Token."""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM
    )
    return encoded_jwt


def create_refresh_token(data: dict):
    """Creates a long-lived Refresh Token."""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(
        days=settings.REFRESH_TOKEN_EXPIRE_DAYS
    )
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM
    )
    return encoded_jwt


def verify_token(token: str) -> TokenData | None:
    """Verifies the token and returns its payload (TokenData)."""
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        username: str | None = payload.get("sub")
        if username is None:
            return None
        return TokenData(username=username)
    except JWTError:
        return None


# --- 5. Dependency for Protected Routes ---
async def get_current_user(
    access_token: Annotated[str | None, Cookie()] = None,
) -> User:
    """
    Dependency to get the access_token from a cookie,
    verify it, and return the corresponding user.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
    )
    if access_token is None:
        raise credentials_exception

    token_data = verify_token(access_token)
    if token_data is None or token_data.username is None:
        raise credentials_exception

    user = get_user(token_data.username)
    if user is None:
        raise credentials_exception

    return user


# --- 6. FastAPI App Initialization and CORS ---
app = FastAPI()

# IMPORTANT: Configure CORS for your frontend
origins = [
    "http://localhost:5173",  # SvelteKit dev server
    "http://127.0.0.1:5173",
    # Add your production frontend URL here
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,  # Allow cookies to be sent
    allow_methods=["*"],
    allow_headers=["*"],
)


# --- 7. API Endpoints ---
@app.post("/api/login")
def login_for_access_token(response: Response, form_data: dict = Body(...)):
    """
    Handles user login, and if successful, sets access and refresh tokens
    in HttpOnly cookies.
    """
    username = form_data.get("username")
    # In a real app, you'd also verify the password here
    if not username or get_user(username) is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )

    # Create tokens
    access_token = create_access_token(data={"sub": username})
    refresh_token = create_refresh_token(data={"sub": username})

    # Set cookies
    # secure=True should be used in production (HTTPS)
    # samesite='lax' or 'strict' for CSRF protection
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        samesite="lax",
        secure=False,
    )
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        samesite="lax",
        secure=False,
    )
    return {"message": "Login successful"}


@app.post("/api/refresh")
def refresh_token_endpoint(
    response: Response, refresh_token: Annotated[str | None, Cookie()] = None
):
    """
    Uses the refresh_token (from a cookie) to issue a new access_token.
    """
    if not refresh_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token not found"
        )

    token_data = verify_token(refresh_token)
    if not token_data or not token_data.username:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token"
        )

    new_access_token = create_access_token(data={"sub": token_data.username})
    response.set_cookie(
        key="access_token",
        value=new_access_token,
        httponly=True,
        samesite="lax",
        secure=False,
    )
    return {"message": "Token refreshed"}


@app.post("/api/logout")
def logout(response: Response):
    """
    Logs out the user by deleting the cookies.
    """
    response.delete_cookie("access_token")
    response.delete_cookie("refresh_token")
    return {"message": "Logout successful"}


@app.get("/api/users/me", response_model=User)
async def read_users_me(current_user: Annotated[User, Depends(get_current_user)]):
    """
    A protected endpoint that requires a valid access_token to access.
    Returns the current user's data.
    """
    return current_user


@app.get("/")
def read_root():
    return {"status": "Backend is running"}
