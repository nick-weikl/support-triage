import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent / "data" / "tickets.db"


def initialize_database():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)

    connection = sqlite3.connect(DB_PATH)

    try:
        with connection:
            connection.execute("""
                CREATE TABLE IF NOT EXISTS tickets (
                    id INTEGER PRIMARY KEY,
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    message TEXT NOT NULL,
                    category TEXT NOT NULL,
                    assigned_team TEXT NOT NULL,
                    urgency REAL NOT NULL,
                    confidence REAL NOT NULL,
                    needs_review INTEGER NOT NULL
                        CHECK (needs_review IN (0, 1))
                )
            """)
            columns = {
                row[1]
                for row in connection.execute("PRAGMA table_info(tickets)")
            }

            for column in ("missing_routing_info", "missing_urgency_info"):
                if column not in columns:
                    connection.execute(
                        f"ALTER TABLE tickets ADD COLUMN {column} REAL"
                    )
    finally:
        connection.close()


def save_ticket(message, result):
    connection = sqlite3.connect(DB_PATH)

    try:
        with connection:
            cursor = connection.execute(
                """
                INSERT INTO tickets (
                    message,
                    category,
                    assigned_team,
                    urgency,
                    confidence,
                    needs_review,
                    missing_routing_info,
                    missing_urgency_info
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    message,
                    result["category"],
                    result["assigned_team"],
                    result["urgency"],
                    result["confidence"],
                    int(result["needs_review"]),
                    result["missing_routing_info"],
                    result["missing_urgency_info"],
                ),
            )

            return cursor.lastrowid
    finally:
        connection.close()


def load_tickets():
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row

    try:
        rows = connection.execute(
            "SELECT * FROM tickets ORDER BY created_at DESC, id DESC"
        ).fetchall()

        return [dict(row) for row in rows]
    finally:
        connection.close()


def update_ticket(ticket_id, message, result):
    connection = sqlite3.connect(DB_PATH)

    try:
        with connection:
            cursor = connection.execute(
                """
                UPDATE tickets
                SET message = ?,
                    category = ?,
                    assigned_team = ?,
                    urgency = ?,
                    confidence = ?,
                    needs_review = ?,
                    missing_routing_info = ?,
                    missing_urgency_info = ?
                WHERE id = ?
                """,
                (
                    message,
                    result["category"],
                    result["assigned_team"],
                    result["urgency"],
                    result["confidence"],
                    int(result["needs_review"]),
                    result["missing_routing_info"],
                    result["missing_urgency_info"],
                    ticket_id,
                ),
            )

            if cursor.rowcount != 1:
                raise ValueError(
                    f"Ticket {ticket_id} was not found; update was not saved."
                )
    finally:
        connection.close()


if __name__ == "__main__":
    initialize_database()
    print(f"Database ready: {DB_PATH}")