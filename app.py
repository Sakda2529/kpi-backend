from fastapi import FastAPI, Depends, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from jose import JWTError
from database import get_db
from auth import verify_password, create_token, decode_token

app = FastAPI(title="KPI Backend API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Startup: create tables ONLY (do not touch passwords)
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
    db.commit()

class LoginRequest(BaseModel):
    username: str
    password: str

# Auth helpers

def get_current_user(authorization: str = Header(..., alias="Authorization")):
    try:
        if not authorization.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="Invalid authorization header")
        token = authorization.replace("Bearer ", "")
        payload = decode_token(token)
        return payload
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    except Exception:
        raise HTTPException(status_code=401, detail="Unauthorized")


def require_roles(*roles):
    def checker(user=Depends(get_current_user)):
        if user.get("role") not in roles:
            raise HTTPException(status_code=403, detail="Forbidden")
        return user
    return checker

@app.get("/")
def root():
    return {"status": "ok", "service": "kpi-backend"}

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/auth/login")
def login(data: LoginRequest):
    db = get_db()
    u = db.execute(
        "SELECT id, username, password_hash, role, team_id FROM users WHERE username=?",
        (data.username,),
    ).fetchone()

    if not u:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    if not verify_password(data.password, u["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_token({
        "user_id": u["id"],
        "username": u["username"],
        "role": u["role"],
        "team_id": u["team_id"],
    })

    return {
        "access_token": token,
        "token_type": "bearer",
        "username": u["username"],
        "role": u["role"],
        "team_id": u["team_id"],
    }

@app.get("/auth/me")
def auth_me(user=Depends(get_current_user)):
    return user

@app.get("/kpi/engineers")
def kpi_engineers(user=Depends(require_roles("admin", "manager", "viewer"))):
    db = get_db()
    rows = db.execute("""
        SELECT e.name AS engineer, COUNT(j.id) AS total_jobs,
        COALESCE(SUM(j.status='done'), 0) AS done,
        COALESCE(SUM(j.status='pending'), 0) AS pending,
        COALESCE(SUM(j.status='in_progress'), 0) AS in_progress,
        ROUND(100.0 * COALESCE(SUM(j.status='done'), 0) / NULLIF(COUNT(j.id), 0), 1) AS completion_rate
        FROM jobs j JOIN engineers e ON e.id = j.engineer_id
        GROUP BY e.id ORDER BY completion_rate DESC
    """).fetchall()
    return [dict(r) for r in rows]

@app.get("/kpi/summary")
def kpi_summary(user=Depends(require_roles("admin", "manager", "viewer"))):
    db = get_db()
    row = db.execute("""
        SELECT COALESCE(SUM(status='done'), 0) AS done,
        COALESCE(SUM(status='pending'), 0) AS pending,
        COALESCE(SUM(status='in_progress'), 0) AS in_progress,
        COALESCE(SUM(status='new'), 0) AS new_jobs
        FROM jobs
    """).fetchone()
    return dict(row)

@app.get("/kpi/weekly")
def kpi_weekly(user=Depends(require_roles("admin", "manager", "viewer"))):
    db = get_db()
    rows = db.execute("""
        SELECT week, ROUND(AVG(completion_rate), 1) AS completion_rate
        FROM kpi_weekly GROUP BY week ORDER BY week
    """).fetchall()
    return [dict(r) for r in rows]

@app.get("/kpi/monthly")
def kpi_monthly(user=Depends(require_roles("admin", "manager", "viewer"))):
    db = get_db()
    rows = db.execute("""
        SELECT month, ROUND(AVG(completion_rate), 1) AS completion_rate
        FROM kpi_monthly GROUP BY month ORDER BY month
    """).fetchall()
    return [dict(r) for r in rows]
