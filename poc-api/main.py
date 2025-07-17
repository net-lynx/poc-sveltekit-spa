# main.py
from fastapi import FastAPI, Response, HTTPException, status, Cookie
from fastapi.middleware.cors import CORSMiddleware
from typing import Annotated

app = FastAPI()

# ## สำคัญ: ตั้งค่า CORS ##
origins = [
    "http://localhost:5173",  # SvelteKit dev server
    # "https://your-svelte-app.com" # Production domain
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,  # <<<<< สำคัญมาก: อนุญาตให้ส่ง Cookie ข้าม Origin
    allow_methods=["*"],
    allow_headers=["*"],
)


# --- ตัวอย่างฟังก์ชันสร้าง Token (ใช้ Pydantic และ python-jose) ---
# (ส่วนนี้เป็น logic การสร้าง JWT ตามปกติ)
def create_access_token(data: dict):
    # ... logic to create a short-lived access token ...
    return "fake_access_token"


def create_refresh_token(data: dict):
    # ... logic to create a long-lived refresh token ...
    return "fake_refresh_token"


def verify_token(token: str):
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated"
        )
    # ... logic to verify token ...
    return {"username": "testuser"}


# ## 1. Login Endpoint ##
@app.post("/api/login")
def login(response: Response):
    # ... ตรวจสอบ username/password ...
    username = "testuser"  # สมมติว่าล็อกอินสำเร็จ

    access_token = create_access_token(data={"sub": username})
    refresh_token = create_refresh_token(data={"sub": username})

    # ตั้งค่า Access Token Cookie
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=True,  # ใช้ True ใน Production
        samesite="lax",
        max_age=60 * 30,  # 30 นาที
    )
    # ตั้งค่า Refresh Token Cookie
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=True,  # ใช้ True ใน Production
        samesite="lax",
        max_age=60 * 60 * 24 * 7,  # 7 วัน
    )
    return {"message": "Login successful"}


# ## 2. Refresh Token Endpoint ##
@app.post("/api/refresh")
def refresh(response: Response, refresh_token: Annotated[str | None, Cookie()] = None):
    if not refresh_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
        )

    # ตรวจสอบ refresh_token
    user_data = verify_token(refresh_token)  # สมมติว่า verify ผ่าน

    # สร้าง access_token ใหม่
    new_access_token = create_access_token(data={"sub": user_data["username"]})

    response.set_cookie(
        key="access_token",
        value=new_access_token,
        httponly=True,
        secure=True,
        samesite="lax",
        max_age=60 * 30,
    )
    return {"message": "Token refreshed"}


# ## 3. Protected Endpoint ##
@app.get("/api/users/me")
def read_users_me(access_token: Annotated[str | None, Cookie()] = None):
    user_info = verify_token(access_token)
    return user_info
