from flask import Flask, render_template, request, redirect, url_for, jsonify
import sqlite3
from pathlib import Path
from datetime import datetime

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "health.db"

app = Flask(__name__)


def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS measurements (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_name TEXT,
            systolic INTEGER NOT NULL,
            diastolic INTEGER NOT NULL,
            heart_rate INTEGER,
            notes TEXT,
            flagged INTEGER NOT NULL DEFAULT 0,
            recorded_at TEXT NOT NULL
        );
        """
    )
    conn.commit()
    conn.close()


@app.route("/", methods=["GET"])
def index():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM measurements ORDER BY recorded_at DESC;")
    measurements = cur.fetchall()
    conn.close()
    return render_template("index.html", measurements=measurements)


@app.route("/add", methods=["POST"])
def add_measurement():
    patient_name = request.form.get("patient_name", "").strip()
    systolic = request.form.get("systolic", "").strip()
    diastolic = request.form.get("diastolic", "").strip()
    heart_rate = request.form.get("heart_rate", "").strip()
    notes = request.form.get("notes", "").strip()

    # Basic validation: systolic & diastolic required and must be integers
    try:
        systolic_val = int(systolic)
        diastolic_val = int(diastolic)
    except ValueError:
        # In a real app, you'd show an error message; for now, just redirect
        return redirect(url_for("index"))

    heart_rate_val = None
    if heart_rate:
        try:
            heart_rate_val = int(heart_rate)
        except ValueError:
            heart_rate_val = None

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO measurements
        (patient_name, systolic, diastolic, heart_rate, notes, flagged, recorded_at)
        VALUES (?, ?, ?, ?, ?, ?, ?);
        """,
        (
            patient_name if patient_name else None,
            systolic_val,
            diastolic_val,
            heart_rate_val,
            notes,
            0,
            datetime.utcnow().isoformat()
        ),
    )
    conn.commit()
    conn.close()
    return redirect(url_for("index"))


@app.route("/delete/<int:measurement_id>", methods=["POST"])
def delete_measurement(measurement_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM measurements WHERE id = ?;", (measurement_id,))
    conn.commit()
    conn.close()
    return redirect(url_for("index"))


@app.route("/api/measurements/<int:measurement_id>/flag", methods=["POST"])
def toggle_flag(measurement_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT flagged FROM measurements WHERE id = ?;", (measurement_id,))
    row = cur.fetchone()
    if row is None:
        conn.close()
        return jsonify({"success": False, "error": "Measurement not found"}), 404

    new_flag = 0 if row["flagged"] else 1
    cur.execute("UPDATE measurements SET flagged = ? WHERE id = ?;", (new_flag, measurement_id))
    conn.commit()
    conn.close()
    return jsonify({"success": True, "flagged": new_flag})

init_db()

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
