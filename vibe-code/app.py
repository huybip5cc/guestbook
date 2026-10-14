"""Bản guestbook một file: Flask + list Python + JSON + Matplotlib."""
import json
from collections import Counter
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from flask import Flask, redirect, render_template_string, request, url_for

ROOT = Path(__file__).resolve().parent
DATA_FILE = ROOT / "data.json"
CHART_FILE = ROOT / "static" / "stats.png"
app = Flask(__name__)
app.secret_key = "guestbook-demo-key"
entries = []


def load_entries():
    global entries
    if DATA_FILE.exists():
        try:
            entries = json.loads(DATA_FILE.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            entries = []


def save_entries():
    DATA_FILE.write_text(json.dumps(entries, ensure_ascii=False, indent=2), encoding="utf-8")


def next_id():
    return max((item["id"] for item in entries), default=0) + 1


def make_chart(counts):
    CHART_FILE.parent.mkdir(parents=True, exist_ok=True)
    names, values = list(counts.keys()), list(counts.values())
    fig, ax = plt.subplots(figsize=(8, 4.2))
    if names:
        ax.bar(names, values, color="#527a5b", width=.65)
        ax.set_ylabel("Số lời nhắn")
        ax.set_xlabel("Người gửi")
        ax.tick_params(axis="x", rotation=25)
        ax.set_ylim(0, max(values) + 1)
    else:
        ax.text(.5, .5, "Chưa có dữ liệu", ha="center", va="center", transform=ax.transAxes)
        ax.set_axis_off()
    fig.tight_layout()
    fig.savefig(CHART_FILE, dpi=140)
    plt.close(fig)


load_entries()

STYLE = ""
INDEX = """<!doctype html><html lang=vi><meta charset=utf-8><meta name=viewport content='width=device-width,initial-scale=1'><title>Sổ lưu bút</title><style>{{style}}</style><main class=wrap><header><div class=eyebrow>GUESTBOOK · LỜI NHẮN TỪ BẠN</div><h1>Để lại một lời chào 👋</h1><p class=intro>Mỗi lời nhắn nhỏ làm nơi này thêm vui.</p></header><a class=button href='{{ url_for("add") }}'>＋ Viết lời nhắn</a> <a class=text-link href='{{ url_for("stats") }}'>Xem thống kê →</a><div class=heading><h2>Tất cả lời nhắn</h2><small>{{entries|length}} lời nhắn</small></div>{% for entry in entries|reverse %}<article class=entry><div class=row><div class=avatar>{{entry.name[0]|upper}}</div><div class=who><strong>{{entry.name}}</strong><span class=meta>ID: {{entry.id}}</span></div><form method=post action='{{url_for("delete", id=entry.id)}}' onsubmit='return confirm("Xóa lời nhắn này?")'><button class=delete>Xóa</button></form></div><p class=body>{{entry.message}}</p></article>{% else %}<div class=empty>Chưa có lời nhắn nào. Hãy là người đầu tiên nhé!</div>{% endfor %}<footer>Dữ liệu được lưu trong data.json.</footer></main></html>"""
ADD = """<!doctype html><html lang=vi><meta charset=utf-8><meta name=viewport content='width=device-width,initial-scale=1'><title>Viết lời nhắn</title><style>{{style}}</style><main class=wrap><div class=eyebrow>GUESTBOOK · LỜI NHẮN TỪ BẠN</div><h1>Viết lời nhắn</h1><p class=intro>Chia sẻ vài dòng với mọi người.</p><section class=panel>{% if error %}<p style='color:#a44'>{{error}}</p>{% endif %}<form method=post><label for=name>Tên của bạn</label><input id=name name=name value='{{name|default("")}}' placeholder='Ví dụ: Linh'><label for=message>Lời nhắn</label><textarea id=message name=message rows=4 placeholder='Bạn muốn chia sẻ điều gì?'>{{message|default("")}}</textarea><button>Gửi lời nhắn ↗</button></form></section><a class=text-link href='{{ url_for("index") }}'>← Trở về sổ lưu bút</a></main></html>"""
STATS = """<!doctype html><html lang=vi><meta charset=utf-8><meta name=viewport content='width=device-width,initial-scale=1'><title>Thống kê</title><style>{{style}}</style><main class=wrap><div class=eyebrow>GUESTBOOK · THỐNG KÊ</div><h1>Những con số nhỏ</h1><p class=intro>Tổng quan lời nhắn và người gửi.</p><section class=panel><h2>Tổng số lời nhắn</h2><p class=stat-number>{{total}}</p></section><section class=panel><h2>Số lời nhắn theo người gửi</h2><img class=chart src='{{url_for("static", filename="stats.png")}}?v={{total}}' alt='Biểu đồ cột số lời nhắn theo người gửi'></section><section class=panel><h2>5 người gửi nhiều lời nhắn nhất</h2>{% if top %}<ol class=top-list>{% for name,count in top %}<li><span>{{name}}</span><strong>{{count}}</strong></li>{% endfor %}</ol>{% else %}<p class=muted>Chưa có dữ liệu.</p>{% endif %}</section><a class=text-link href='{{ url_for("index") }}'>← Trở về sổ lưu bút</a></main></html>"""


@app.get("/")
def index():
    return render_template_string(INDEX, entries=entries, style=STYLE)


@app.route("/add", methods=["GET", "POST"])
def add():
    if request.method == "GET":
        return render_template_string(ADD, style=STYLE)
    name, message = request.form.get("name", "").strip(), request.form.get("message", "").strip()
    if not name or not message:
        return render_template_string(ADD, style=STYLE, error="Vui lòng nhập cả tên và lời nhắn.", name=name, message=message), 400
    entries.append({"id": next_id(), "name": name, "message": message})
    save_entries()
    return redirect(url_for("index"))


@app.post("/delete/<int:id>")
def delete(id):
    global entries
    entries = [entry for entry in entries if entry["id"] != id]
    save_entries()
    return redirect(url_for("index"))


@app.get("/stats")
def stats():
    counts = Counter(item["name"] for item in entries)
    make_chart(counts)
    return render_template_string(STATS, style=STYLE, total=len(entries), top=counts.most_common(5))


if __name__ == "__main__":
    app.run(debug=True)
