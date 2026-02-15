from flask import Flask, request
from flask_jwt_extended import (
    JWTManager,
    create_access_token,
    jwt_required,
    get_jwt_identity
)
from flask_cors import CORS
from config import DB_CONFIG, JWT_SECRET_KEY
import mysql.connector
import bcrypt
from datetime import timedelta

app = Flask(__name__)

# JWT Config
app.config["JWT_SECRET_KEY"] = JWT_SECRET_KEY
jwt = JWTManager(app)
CORS(app)

# ---------------- DB ----------------
def get_db_connection():
    return mysql.connector.connect(
        host=DB_CONFIG["host"],
        user=DB_CONFIG["user"],
        password=DB_CONFIG["password"],
        database=DB_CONFIG["database"]
    )

# ---------------- HOME ----------------
@app.route("/")
def home():
    return {"message": "Secure Login Dashboard Backend | STEP 5 OK"}

# ---------------- HELPERS ----------------
def log_login_attempt(user_id, ip, success):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO login_attempts (user_id, ip_address, success) VALUES (%s,%s,%s)",
        (user_id, ip, success)
    )
    conn.commit()
    cursor.close()
    conn.close()

def log_security_event(event_type, description, ip):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO security_logs (event_type, description, ip_address) VALUES (%s,%s,%s)",
        (event_type, description, ip)
    )
    conn.commit()
    cursor.close()
    conn.close()

def failed_attempts_last_15_min(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT COUNT(*) FROM login_attempts
        WHERE user_id=%s AND success=FALSE
        AND attempt_time >= NOW() - INTERVAL 15 MINUTE
    """, (user_id,))
    count = cursor.fetchone()[0]
    cursor.close()
    conn.close()
    return count

def auto_unlock_user(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT COUNT(*) FROM login_attempts
        WHERE user_id=%s AND success=FALSE
        AND attempt_time >= NOW() - INTERVAL 15 MINUTE
    """, (user_id,))
    recent_fails = cursor.fetchone()[0]

    if recent_fails < 5:
        cursor.execute(
            "UPDATE users SET is_locked=FALSE WHERE id=%s",
            (user_id,)
        )
        conn.commit()

    cursor.close()
    conn.close()

# ---------------- REGISTER ----------------
@app.route("/register", methods=["POST"])
def register():
    data = request.json
    username = data.get("username")
    email = data.get("email")
    password = data.get("password")

    if not username or not email or not password:
        return {"error": "Missing fields"}, 400

    hashed_pw = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO users (username, email, password_hash) VALUES (%s,%s,%s)",
        (username, email, hashed_pw.decode())
    )
    conn.commit()
    cursor.close()
    conn.close()

    return {"message": "User registered successfully"}, 201

# ---------------- LOGIN ----------------
@app.route("/login", methods=["POST"])
def login():
    data = request.json
    email = data.get("email")
    password = data.get("password")
    ip = request.remote_addr

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM users WHERE email=%s", (email,))
    user = cursor.fetchone()
    cursor.close()
    conn.close()

    if not user:
        log_security_event("LOGIN_FAIL", "Invalid email", ip)
        return {"error": "Invalid credentials"}, 401

    auto_unlock_user(user["id"])

    if user["is_locked"]:
        return {"error": "Account locked"}, 403

    if bcrypt.checkpw(password.encode(), user["password_hash"].encode()):
        log_login_attempt(user["id"], ip, True)

        token = create_access_token(
            identity={
                "user_id": user["id"],
                "email": user["email"],
                "role": user["role"]
            },
            expires_delta=timedelta(minutes=30)
        )
        return {"token": token}, 200

    log_login_attempt(user["id"], ip, False)
    return {"error": "Invalid credentials"}, 401

# ---------------- DASHBOARD ----------------
@app.route("/dashboard", methods=["GET"])
@jwt_required()
def dashboard():
    user = get_jwt_identity()
    return {"message": "Welcome to Dashboard", "user": user}, 200

# ---------------- DASHBOARD APIs ----------------

# Failed logins in last 24 hours
@app.route("/dashboard/failed-logins", methods=["GET"])
@jwt_required()
def failed_logins_24h():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT COUNT(*) FROM login_attempts
        WHERE success = FALSE
        AND attempt_time >= NOW() - INTERVAL 1 DAY
    """)
    count = cursor.fetchone()[0]
    cursor.close()
    conn.close()
    return {"failed_logins_24h": count}, 200

# Locked accounts count
@app.route("/dashboard/locked-accounts", methods=["GET"])
@jwt_required()
def locked_accounts():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT COUNT(*) FROM users WHERE is_locked = TRUE
    """)
    count = cursor.fetchone()[0]
    cursor.close()
    conn.close()
    return {"locked_accounts": count}, 200

# Recent security logs
@app.route("/dashboard/security-logs", methods=["GET"])
@jwt_required()
def dashboard_security_logs():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT event_type, description, ip_address, created_at
        FROM security_logs
        ORDER BY created_at DESC
        LIMIT 10
    """)
    logs = cursor.fetchall()
    cursor.close()
    conn.close()
    return {"security_logs": logs}, 200

# Summary API (frontend ke liye best)
@app.route("/dashboard/summary", methods=["GET"])
@jwt_required()
def dashboard_summary():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT COUNT(*) FROM login_attempts
        WHERE success = FALSE
        AND attempt_time >= NOW() - INTERVAL 1 DAY
    """)
    failed_24h = cursor.fetchone()[0]

    cursor.execute("""
        SELECT COUNT(*) FROM users WHERE is_locked = TRUE
    """)
    locked_users = cursor.fetchone()[0]

    cursor.close()
    conn.close()

    return {
        "failed_logins_24h": failed_24h,
        "locked_accounts": locked_users
    }, 200

# ---------------- ADMIN PANEL ----------------
@app.route("/admin", methods=["GET"])
@jwt_required()
def admin_panel():
    user = get_jwt_identity()
    if user.get("role") != "admin":
        return {"error": "Admin access only"}, 403
    return {"message": "Welcome Admin"}, 200

# ---------------- ADMIN UNLOCK USER ----------------
@app.route("/admin/unlock", methods=["POST"])
@jwt_required()
def admin_unlock():
    admin = get_jwt_identity()

    if admin.get("role") != "admin":
        return {"error": "Admin access only"}, 403

    data = request.json
    user_id = data.get("user_id")

    if not user_id:
        return {"error": "user_id required"}, 400

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE users SET is_locked=FALSE WHERE id=%s",
        (user_id,)
    )
    conn.commit()
    cursor.close()
    conn.close()

    return {"message": "User unlocked successfully"}, 200

# ---------------- RUN ----------------
if __name__ == "__main__":
    app.run(debug=True)
