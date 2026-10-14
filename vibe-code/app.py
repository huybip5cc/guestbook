"""Quick single-file guestbook demo built with Flask and SQLite."""
import os
import secrets
import sqlite3
from pathlib import Path

from flask import Flask, abort, flash, redirect, render_template_string, request, session, url_for

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", secrets.token_hex(32))
DB = Path(os.environ.get("GUESTBOOK_DB", Path(__file__).with_name("guestbook.db")))
DB.parent.mkdir(parents=True, exist_ok=True)

with sqlite3.connect(DB) as connection:
    connection.execute("CREATE TABLE IF NOT EXISTS messages (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, message TEXT NOT NULL, created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP)")

PAGE = """<!doctype html><html lang=vi><meta charset=utf-8><meta name=viewport content='width=device-width,initial-scale=1'><title>Sổ lưu bút</title>
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Playfair+Display:wght@600;700&display=swap');
*{box-sizing:border-box}body{margin:0;background:radial-gradient(ellipse at 85% 3%,#e6eee4,transparent 32%),#f5f6f1;color:#28372f;font:15px 'DM Sans',sans-serif}.wrap{max-width:720px;width:calc(100% - 36px);margin:68px auto 40px}.eyebrow{font-size:11px;letter-spacing:2px;color:#76927e;font-weight:bold}h1{font:700 clamp(36px,7vw,54px) 'Playfair Display',serif;letter-spacing:-1.5px;margin:12px 0 8px;color:#20362a}.intro{color:#738078;margin:0 0 30px}.card,.entry,.empty{background:#fff;border:1px solid #e6eae4;border-radius:13px}.card{padding:24px 27px;box-shadow:0 12px 35px #34452e0a}h2{font-size:16px;margin:0 0 18px}label{display:block;font-size:12px;font-weight:700;margin:14px 0 7px}input,textarea{width:100%;border:1px solid #e0e5de;background:#fbfcfa;border-radius:8px;padding:12px;font:inherit;font-size:14px;outline:none}input:focus,textarea:focus{border-color:#78977e}textarea{resize:vertical}button{font:inherit;cursor:pointer;border:0}.send{margin-top:14px;background:#315a40;color:white;border-radius:8px;padding:12px 17px;font-size:13px;font-weight:bold}.send span{margin-left:12px}.heading{display:flex;justify-content:space-between;align-items:center;margin:32px 0 12px}.heading h2{margin:0}.heading small,.meta{color:#98a19a;font-size:11px}.entry{padding:16px 18px;margin:10px 0}.row{display:flex;align-items:center;gap:10px}.avatar{display:grid;place-items:center;width:35px;height:35px;border-radius:50%;background:#e7efe8;color:#42664b;font-weight:bold}.who{display:grid;gap:3px;flex:1;font-size:13px}.delete{background:transparent;color:#a47770;font-size:11px}.body{white-space:pre-wrap;overflow-wrap:anywhere;line-height:1.65;font-size:14px;margin:12px 0 1px 45px}.empty{text-align:center;padding:30px;color:#7d8980;font-size:13px}.notice{padding:11px 14px;border-radius:8px;font-size:13px}.success{background:#e8f2e9;color:#315a40}.error{background:#fff0eb;color:#9b5141}footer{text-align:center;color:#9ba39c;font-size:11px;padding:26px}@media(max-width:520px){.wrap{margin-top:40px}.card{padding:21px}.body{margin-left:0}}
</style><main class=wrap><header><div class=eyebrow>GUESTBOOK · LỜI NHẮN TỪ BẠN</div><h1>Để lại một lời chào 👋</h1><p class=intro>Mỗi lời nhắn nhỏ làm nơi này thêm vui.</p></header>
{% for category,notice in get_flashed_messages(with_categories=true) %}<p class='notice {{category}}'>{{notice}}</p>{% endfor %}
<section class=card><h2>Viết lời nhắn</h2><form method=post action='{{ url_for("add") }}'><input type=hidden name=csrf_token value='{{token}}'><label for=name>Tên của bạn</label><input id=name name=name maxlength=80 placeholder='Ví dụ: Linh' required><label for=message>Lời nhắn</label><textarea id=message name=message rows=4 maxlength=1000 placeholder='Bạn muốn chia sẻ điều gì?' required></textarea><button class=send>Gửi lời nhắn <span>↗</span></button></form></section>
<div class=heading><h2>Lời nhắn mới nhất</h2><small>{{messages|length}} lời nhắn</small></div>
{% for item in messages %}<article class=entry><div class=row><div class=avatar>{{item.name[0]|upper}}</div><div class=who><strong>{{item.name}}</strong><span class=meta>#{{item.id}} · {{item.created_at}}</span></div><form method=post action='{{url_for("delete", message_id=item.id)}}' onsubmit='return confirm("Xóa lời nhắn này?")'><input type=hidden name=csrf_token value='{{token}}'><button class=delete aria-label='Xóa lời nhắn {{item.id}}'>Xóa</button></form></div><p class=body>{{item.message}}</p></article>{% else %}<div class=empty>Chưa có lời nhắn nào. Hãy là người đầu tiên nhé!</div>{% endfor %}<footer>Lưu bút được lưu bằng SQLite.</footer></main></html>"""


def check_token():
    if not secrets.compare_digest(request.form.get("csrf_token", ""), session.get("csrf_token", "")):
        abort(400, "Invalid form token")


@app.get("/")
def home():
    token = session.setdefault("csrf_token", secrets.token_hex(32))
    with sqlite3.connect(DB) as connection:
        connection.row_factory = sqlite3.Row
        messages = connection.execute("SELECT id,name,message,created_at FROM messages ORDER BY id DESC").fetchall()
    return render_template_string(PAGE, messages=messages, token=token)


@app.post("/messages")
def add():
    check_token()
    name, message = request.form.get("name", "").strip(), request.form.get("message", "").strip()
    if not name or not message or len(name) > 80 or len(message) > 1000:
        flash("Vui lòng nhập tên (tối đa 80 ký tự) và lời nhắn (tối đa 1000 ký tự).", "error")
    else:
        with sqlite3.connect(DB) as connection:
            connection.execute("INSERT INTO messages(name,message) VALUES(?,?)", (name, message))
        flash("Đã lưu lời nhắn của bạn!", "success")
    return redirect(url_for("home"))


@app.post("/messages/<int:message_id>/delete")
def delete(message_id):
    check_token()
    with sqlite3.connect(DB) as connection:
        connection.execute("DELETE FROM messages WHERE id=?", (message_id,))
    flash(f"Đã xóa lời nhắn #{message_id} (nếu tồn tại).", "success")
    return redirect(url_for("home"))


if __name__ == "__main__":
    app.run(debug=os.environ.get("FLASK_DEBUG") == "1")
