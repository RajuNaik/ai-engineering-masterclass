import sqlite3
from datetime import datetime, timezone
from pathlib import Path


# ---------------------------------------------------------
# Persistent conversation store
# ---------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "conversation_store.db"


def utc_now():
    return datetime.now(timezone.utc).isoformat()


def get_connection():
    connection = sqlite3.connect(DB_PATH)
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def initialize_database():
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS conversations (
            conversation_id TEXT PRIMARY KEY,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            summary TEXT,
            summary_through_message_id INTEGER
        )
        """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS messages (
            message_id INTEGER PRIMARY KEY AUTOINCREMENT,
            conversation_id TEXT NOT NULL,
            role TEXT NOT NULL CHECK (role IN ('user', 'assistant')),
            content TEXT NOT NULL,
            created_at TEXT NOT NULL,
            FOREIGN KEY (conversation_id)
                REFERENCES conversations(conversation_id)
                ON DELETE CASCADE
        )
        """
    )

    cursor.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_messages_conversation
        ON messages (conversation_id, message_id)
        """
    )

    connection.commit()
    connection.close()


def create_conversation(conversation_id):
    now = utc_now()

    connection = get_connection()
    connection.execute(
        """
        INSERT INTO conversations (
            conversation_id,
            created_at,
            updated_at,
            summary,
            summary_through_message_id
        )
        VALUES (?, ?, ?, NULL, NULL)
        """,
        (conversation_id, now, now),
    )
    connection.commit()
    connection.close()


def conversation_exists(conversation_id):
    connection = get_connection()
    row = connection.execute(
        """
        SELECT 1
        FROM conversations
        WHERE conversation_id = ?
        """,
        (conversation_id,),
    ).fetchone()
    connection.close()
    return row is not None


def save_message(conversation_id, role, content):
    now = utc_now()

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        INSERT INTO messages (
            conversation_id,
            role,
            content,
            created_at
        )
        VALUES (?, ?, ?, ?)
        """,
        (conversation_id, role, content, now),
    )

    cursor.execute(
        """
        UPDATE conversations
        SET updated_at = ?
        WHERE conversation_id = ?
        """,
        (now, conversation_id),
    )

    message_id = cursor.lastrowid

    connection.commit()
    connection.close()

    return message_id


def load_messages(conversation_id):
    connection = get_connection()
    rows = connection.execute(
        """
        SELECT message_id, role, content, created_at
        FROM messages
        WHERE conversation_id = ?
        ORDER BY message_id
        """,
        (conversation_id,),
    ).fetchall()
    connection.close()

    return [
        {
            "message_id": row[0],
            "role": row[1],
            "content": row[2],
            "created_at": row[3],
        }
        for row in rows
    ]


def get_conversation_state(conversation_id):
    connection = get_connection()
    row = connection.execute(
        """
        SELECT summary, summary_through_message_id
        FROM conversations
        WHERE conversation_id = ?
        """,
        (conversation_id,),
    ).fetchone()
    connection.close()

    if row is None:
        return {"summary": "", "summary_through_message_id": None}

    return {
        "summary": row[0] or "",
        "summary_through_message_id": row[1],
    }


def save_conversation_summary(
    conversation_id,
    summary,
    summary_through_message_id,
):
    now = utc_now()

    connection = get_connection()
    connection.execute(
        """
        UPDATE conversations
        SET summary = ?,
            summary_through_message_id = ?,
            updated_at = ?
        WHERE conversation_id = ?
        """,
        (
            summary,
            summary_through_message_id,
            now,
            conversation_id,
        ),
    )
    connection.commit()
    connection.close()
