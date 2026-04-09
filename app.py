from fastapi import FastAPI, Depends, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from jose import JWTError

from database import get_db
from auth import verify_password, create_token, decode_token, hash_password

# ✅ สร้าง app ก่อน
app = FastAPI(title="KPI Backend API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ แล้วค่อยใช้ @app ได้
@app.on_event("startup")
def startup():
    db = get_db()
    db.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password_hash TEXT,
            role TEXT,
            team_id INTEGER
        );
        CREATE TABLE IF NOT EXISTS engineers (
            id INTEGER PRIMARY KEY,
            name TEXT,
            team_id INTEGER
        );
        CREATE TABLE IF NOT EXISTS jobs (
            id INTEGER PRIMARY KEY,
            engineer_id INTEGER,
            status TEXT,
            created_at DATE,
            completed_at DATE
        );
        CREATE TABLE IF NOT EXISTS kpi_weekly (
            week TEXT,
            engineer_id INTEGER,
            completion_rate REAL
        );
        CREATE TABLE IF NOT EXISTS kpi_monthly (
            month TEXT,
            engineer_id INTEGER,
            completion_rate REAL
        );
    """)
    db.execute(
        "INSERT OR IGNORE INTO users (username, password_hash, role) VALUES ('admin', ?, 'admin')",
        (hash_password("1234"),)
    )
    db.commit()

# ... routes ที่เหลือตามเดิม