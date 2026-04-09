# เพิ่ม import ด้านบน
from auth import verify_password, create_token, decode_token, hash_password

# เพิ่มก่อน @app.get("/")
@app.on_event("startup")
def startup():
    db = get_db()
    # สร้างตารางถ้ายังไม่มี
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
    # seed admin ถ้ายังไม่มี
    db.execute("""
        INSERT OR IGNORE INTO users (username, password_hash, role)
        VALUES ('admin', ?, 'admin')
    """, (hash_password("1234"),))
    db.commit()