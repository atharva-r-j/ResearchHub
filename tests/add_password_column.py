import hashlib
import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()
conn = psycopg2.connect(
    dbname=os.getenv("DB_NAME"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    host=os.getenv("DB_HOST"),
    port=os.getenv("DB_PORT"),
)
cur = conn.cursor()

# Add column if it doesn't exist yet
cur.execute("ALTER TABLE users ADD COLUMN IF NOT EXISTS password_hash VARCHAR(64) NOT NULL DEFAULT '';")

def hash_pw(pw):
    return hashlib.sha256(pw.encode()).hexdigest()

# Give every existing user the demo password  "password123"
users = [("atharva_j", "password123"), ("tanisha", "password123"), ("prof_mehta", "password123")]
for username, pw in users:
    cur.execute("UPDATE users SET password_hash = %s WHERE username = %s;", (hash_pw(pw), username))

conn.commit()

cur.execute("SELECT username, email, full_name, password_hash FROM users;")
for row in cur.fetchall():
    print(row[0], "|", row[1], "| hash:", row[3][:20] + "...")

cur.close()
conn.close()
print("Done!")
