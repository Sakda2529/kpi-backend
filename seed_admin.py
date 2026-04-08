import sqlite3
from auth import hash_password

conn = sqlite3.connect("kpi.db")
cur = conn.cursor()

cur.execute("""
INSERT OR IGNORE INTO users (username, password_hash, role)
VALUES ('admin', ?, 'admin')
""", (hash_password("1234"),))

conn.commit()
conn.close()
print("✅ Admin user created")