import os
import secrets
import sqlite3
from pathlib import Path

from flask import Flask, abort, flash, redirect, render_template, request, session, url_for

BASE_DIR = Path(__file__).resolve().parent
app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", secrets.token_hex(32))
DATABASE = Path(os.environ.get("GUESTBOOK_DB", BASE_DIR / "guestbook.db"))


def connect_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def initialize_db():
    DATABASE.parent.mkdir(parents=True, exist_ok=True)
    with connect_db() as conn:
        conn.execute("""CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            message TEXT NOT NULL,
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        )""")


@app.get("/")
def index():
    token = session.setdefault("csrf_token", secrets.token_hex(32))
    with connect_db() as conn:
        messages = conn.execute("SELECT id, name, message, created_at FROM messages ORDER BY id DESC").fetchall()
    return render_template("index.html", messages=messages, csrf_token=token)


def verify_csrf():
    if not secrets.compare_digest(request.form.get("csrf_token", ""), session.get("csrf_token", "")):
        abort(400, "Invalid form token")


@app.post("/messages")
def add_message():
    verify_csrf()
    name = request.form.get("name", "").strip()
    message = request.form.get("message", "").strip()
    if not name or not message or len(name) > 80 or len(message) > 1000:
        flash("Vui lòng nhập tên (tối đa 80 ký tự) và lời nhắn (tối đa 1000 ký tự).", "error")
    else:
        with connect_db() as conn:
            conn.execute("INSERT INTO messages (name, message) VALUES (?, ?)", (name, message))
        flash("Đã lưu lời nhắn của bạn!", "success")
    return redirect(url_for("index"))


@app.post("/messages/<int:message_id>/delete")
def delete_message(message_id):
    verify_csrf()
    with connect_db() as conn:
        conn.execute("DELETE FROM messages WHERE id = ?", (message_id,))
    flash(f"Đã xóa lời nhắn #{message_id} (nếu tồn tại).", "success")
    return redirect(url_for("index"))


initialize_db()

if __name__ == "__main__":
    app.run(debug=os.environ.get("FLASK_DEBUG") == "1")
