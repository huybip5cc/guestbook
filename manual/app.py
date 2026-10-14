import json
from collections import Counter
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from flask import Flask, flash, redirect, render_template, request, url_for

BASE_DIR = Path(__file__).resolve().parent
DATA_FILE = BASE_DIR / "data.json"
CHART_FILE = BASE_DIR / "static" / "stats.png"
app = Flask(__name__)
app.secret_key = "guestbook-demo-key"

# Buổi 1: dữ liệu nằm trong list Python toàn cục.
# Buổi 2: list được nạp từ và ghi lại vào file JSON.
entries = []


def load_entries():
    global entries
    if DATA_FILE.exists():
        try:
            entries = json.loads(DATA_FILE.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            entries = []
    else:
        entries = []


def save_entries():
    DATA_FILE.write_text(json.dumps(entries, ensure_ascii=False, indent=2), encoding="utf-8")


def next_id():
    return max((entry["id"] for entry in entries), default=0) + 1


def create_chart(counts):
    CHART_FILE.parent.mkdir(parents=True, exist_ok=True)
    names = list(counts.keys())
    values = list(counts.values())
    fig, ax = plt.subplots(figsize=(8, 4.2))
    if names:
        ax.bar(names, values, color="#527a5b", width=0.65)
        ax.set_ylabel("Số lời nhắn")
        ax.set_xlabel("Người gửi")
        ax.tick_params(axis="x", rotation=25)
        ax.set_ylim(0, max(values) + 1)
    else:
        ax.text(0.5, 0.5, "Chưa có dữ liệu", ha="center", va="center", transform=ax.transAxes)
        ax.set_axis_off()
    fig.tight_layout()
    fig.savefig(CHART_FILE, dpi=140)
    plt.close(fig)


load_entries()


@app.get("/")
def index():
    return render_template("index.html", entries=entries)


@app.route("/add", methods=["GET", "POST"])
def add():
    if request.method == "GET":
        return render_template("add.html")
    name = request.form.get("name", "").strip()
    message = request.form.get("message", "").strip()
    if not name or not message:
        return render_template("add.html", error="Vui lòng nhập cả tên và lời nhắn.", name=name, message=message), 400
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
    counts = Counter(entry["name"] for entry in entries)
    top_senders = counts.most_common(5)
    create_chart(counts)
    return render_template("stats.html", total=len(entries), top_senders=top_senders)


if __name__ == "__main__":
    app.run(debug=True)
