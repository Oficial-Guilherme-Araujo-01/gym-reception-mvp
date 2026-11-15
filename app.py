import sqlite3
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)
DB_NAME = "gym.db"

def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS members (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            plan TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'Ativo'
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS checkins (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            member_id INTEGER NOT NULL,
            checkin_time TEXT NOT NULL,
            FOREIGN KEY (member_id) REFERENCES members (id)
        )
    """)
    conn.commit()
    conn.close()

@app.route("/")
def index():
    conn = get_db_connection()
    members = conn.execute("SELECT * FROM members ORDER BY id DESC").fetchall()
    checkins = conn.execute("""
        SELECT c.id, m.name, m.plan, c.checkin_time
        FROM checkins c
        JOIN members m ON c.member_id = m.id
        ORDER BY c.id DESC LIMIT 10
    """).fetchall()
    conn.close()
    return render_template("index.html", members=members, checkins=checkins)

@app.route("/register", methods=["POST"])
def register():
    name = request.form.get("name", "").strip()
    plan = request.form.get("plan", "Mensal")
    if name:
        conn = get_db_connection()
        conn.execute("INSERT INTO members (name, plan) VALUES (?, ?)", (name, plan))
        conn.commit()
        conn.close()
    return redirect(url_for("index"))

@app.route("/checkin/<int:member_id>", methods=["POST"])
def checkin(member_id):
    conn = get_db_connection()
    now = datetime.now().strftime("%d/%m/%Y %H:%M")
    conn.execute("INSERT INTO checkins (member_id, checkin_time) VALUES (?, ?)", (member_id, now))
    conn.commit()
    conn.close()
    return redirect(url_for("index"))

if __name__ == "__main__":
    init_db()
    app.run(debug=True)