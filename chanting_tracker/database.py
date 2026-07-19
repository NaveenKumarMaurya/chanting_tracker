import sqlite3
from datetime import date, timedelta
from pathlib import Path

import pandas as pd

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "data" / "chanting.db"


def get_connection():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_connection()
    with conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS devotees (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                phone TEXT,
                email TEXT,
                notes TEXT,
                is_active INTEGER DEFAULT 1,
                created_at TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS reports (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                devotee_id TEXT NOT NULL,
                devotee_name TEXT NOT NULL,
                report_date TEXT NOT NULL,
                japa_count INTEGER DEFAULT 0,
                chanting_hours REAL DEFAULT 0,
                spiritual_notes TEXT,
                submitted_at TEXT NOT NULL,
                UNIQUE(devotee_id, report_date)
            )
            """
        )

        existing_columns = {
            row["name"]
            for row in conn.execute("PRAGMA table_info(reports)").fetchall()
        }
        if "chanting_completion_time" not in existing_columns:
            conn.execute(
                "ALTER TABLE reports ADD COLUMN chanting_completion_time TEXT DEFAULT ''"
            )
    conn.close()
    cleanup_old_records(days=7)


def cleanup_old_records(days=7):
    cutoff = (date.today() - timedelta(days=days - 1)).isoformat()
    conn = get_connection()
    with conn:
        cursor = conn.execute("DELETE FROM reports WHERE report_date < ?", (cutoff,))
    conn.close()
    return cursor.rowcount


def seed_sample_data():
    conn = get_connection()
    with conn:
        count = conn.execute("SELECT COUNT(*) AS total FROM devotees").fetchone()["total"]
        if count == 0:
            conn.executemany(
                """
                INSERT INTO devotees (name, phone, email, notes, is_active, created_at)
                VALUES (?, ?, ?, ?, 1, ?)
                """,
                [
                    ("Aarav Sharma", "9999999991", "aarav@example.com", "Regular", date.today().isoformat()),
                    ("Bhavya Nair", "9999999992", "bhavya@example.com", "Morning schedule", date.today().isoformat()),
                    ("Chaitra Rao", "9999999993", "chaitra@example.com", "Vedic chanting", date.today().isoformat()),
                    ("Divya Iyer", "9999999994", "divya@example.com", "Evening practice", date.today().isoformat()),
                    ("Eshwar Kumar", "9999999995", "eshwar@example.com", "Volunteer", date.today().isoformat()),
                ],
            )
    conn.close()


def add_devotee(name, phone="", email="", notes=""):
    conn = get_connection()
    with conn:
        cursor = conn.execute(
            """
            INSERT INTO devotees (name, phone, email, notes, is_active, created_at)
            VALUES (?, ?, ?, ?, 1, ?)
            """,
            (name, phone, email, notes, date.today().isoformat()),
        )
        inserted_id = cursor.lastrowid
    conn.close()
    return inserted_id


def get_devotees():
    conn = get_connection()
    rows = conn.execute(
        "SELECT id, name, phone, email, notes, is_active FROM devotees ORDER BY name ASC"
    ).fetchall()
    conn.close()
    return [
        {
            "id": str(row["id"]),
            "name": row["name"],
            "phone": row["phone"],
            "email": row["email"],
            "notes": row["notes"],
            "is_active": row["is_active"],
        }
        for row in rows
    ]


def get_last_7_days_dates():
    today = date.today()
    return [(today - timedelta(days=i)).isoformat() for i in range(6, -1, -1)]


def save_report(devotee_id, report_date, japa_count, chanting_hours, spiritual_notes, chanting_completion_time=""):
    conn = get_connection()
    devotee = conn.execute(
        "SELECT name FROM devotees WHERE id = ?",
        (int(devotee_id),),
    ).fetchone()
    if not devotee:
        conn.close()
        raise ValueError("Devotee not found")

    with conn:
        conn.execute(
            """
            INSERT INTO reports (devotee_id, devotee_name, report_date, japa_count, chanting_hours, chanting_completion_time, spiritual_notes, submitted_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(devotee_id, report_date)
            DO UPDATE SET
                devotee_name = excluded.devotee_name,
                japa_count = excluded.japa_count,
                chanting_hours = excluded.chanting_hours,
                chanting_completion_time = excluded.chanting_completion_time,
                spiritual_notes = excluded.spiritual_notes,
                submitted_at = excluded.submitted_at
            """,
            (
                str(devotee_id),
                devotee["name"],
                report_date,
                int(japa_count),
                float(chanting_hours),
                chanting_completion_time,
                spiritual_notes,
                date.today().isoformat(),
            ),
        )
    conn.close()


def get_reports_for_last_7_days():
    dates = get_last_7_days_dates()
    placeholders = ", ".join("?" for _ in dates)
    conn = get_connection()
    rows = conn.execute(
        f"""
        SELECT report_date, devotee_name, japa_count, chanting_hours, chanting_completion_time, spiritual_notes
        FROM reports
        WHERE report_date IN ({placeholders})
        ORDER BY report_date DESC
        """,
        dates,
    ).fetchall()
    conn.close()
    return pd.DataFrame([
        {
            "report_date": row["report_date"],
            "devotee_name": row["devotee_name"],
            "japa_count": row["japa_count"],
            "chanting_hours": row["chanting_hours"],
            "chanting_completion_time": row["chanting_completion_time"],
            "spiritual_notes": row["spiritual_notes"],
        }
        for row in rows
    ])


def get_dashboard_summary():
    dates = get_last_7_days_dates()
    conn = get_connection()
    total_devotees = conn.execute("SELECT COUNT(*) AS total FROM devotees WHERE is_active = 1").fetchone()["total"]
    total_reports = conn.execute(
        f"SELECT COUNT(*) AS total FROM reports WHERE report_date IN ({', '.join('?' for _ in dates)})",
        dates,
    ).fetchone()["total"]
    completed_today = conn.execute(
        "SELECT COUNT(DISTINCT devotee_id) AS total FROM reports WHERE report_date = ?",
        (date.today().isoformat(),),
    ).fetchone()["total"]
    conn.close()

    return {
        "total_devotees": total_devotees,
        "total_reports": total_reports,
        "completed_today": completed_today,
        "missing_today": max(0, total_devotees - completed_today),
    }


def get_missing_report_stats():
    dates = get_last_7_days_dates()
    conn = get_connection()
    active_devotees = conn.execute(
        "SELECT id, name FROM devotees WHERE is_active = 1"
    ).fetchall()
    output = []

    for report_date in dates:
        submitted_rows = conn.execute(
            "SELECT devotee_id FROM reports WHERE report_date = ?",
            (report_date,),
        ).fetchall()
        submitted_ids = {str(row["devotee_id"]) for row in submitted_rows}
        missing_names = [row["name"] for row in active_devotees if str(row["id"]) not in submitted_ids]
        output.append({
            "date": report_date,
            "missing_count": len(missing_names),
            "missing_names": ", ".join(missing_names),
        })

    conn.close()
    return pd.DataFrame(output)


def get_retention_days():
    return 7