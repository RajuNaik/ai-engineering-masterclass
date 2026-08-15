import sqlite3
from datetime import datetime, timezone
from pathlib import Path


# ---------------------------------------------------------
# Structured Memory Store - Learning Implementation
# ---------------------------------------------------------
#
# This is intentionally separate from chat-history storage.
#
# messages table  -> raw conversation events
# memories table  -> durable information derived from events
#
# Production systems may use PostgreSQL, Cosmos DB, etc.
# SQLite is used here so we can inspect the complete flow locally.
# ---------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "conversation_store.db"

TEST_CONVERSATION_ID = "2db64137-5c05-4036-8159-4187ef4a9161"
TEST_USER_ID = "raju"


def utc_now():
    return datetime.now(timezone.utc).isoformat()


def get_connection():
    connection = sqlite3.connect(DB_PATH)
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def initialize_memory_table():
    """Create the structured memory table without changing chat history."""
    connection = get_connection()

    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS memories (
            memory_id INTEGER PRIMARY KEY AUTOINCREMENT,
            conversation_id TEXT,
            user_id TEXT NOT NULL,
            memory_type TEXT NOT NULL,
            memory_key TEXT NOT NULL,
            memory_value TEXT NOT NULL,
            confidence REAL,
            source_message_id INTEGER,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            is_active INTEGER NOT NULL DEFAULT 1
                CHECK (is_active IN (0, 1)),
            FOREIGN KEY (conversation_id)
                REFERENCES conversations(conversation_id)
                ON DELETE SET NULL
        )
        """
    )

    connection.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_memories_user_active
        ON memories (user_id, is_active)
        """
    )

    connection.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_memories_key
        ON memories (user_id, memory_key, is_active)
        """
    )

    connection.commit()
    connection.close()


def upsert_memory(
    user_id,
    memory_type,
    memory_key,
    memory_value,
    confidence,
    conversation_id=None,
    source_message_id=None,
):
    """Create a memory or update the active memory with the same key."""
    now = utc_now()
    connection = get_connection()

    existing = connection.execute(
        """
        SELECT memory_id
        FROM memories
        WHERE user_id = ?
          AND memory_key = ?
          AND is_active = 1
        ORDER BY memory_id DESC
        LIMIT 1
        """,
        (user_id, memory_key),
    ).fetchone()

    if existing:
        connection.execute(
            """
            UPDATE memories
            SET memory_type = ?,
                memory_value = ?,
                confidence = ?,
                conversation_id = ?,
                source_message_id = ?,
                updated_at = ?
            WHERE memory_id = ?
            """,
            (
                memory_type,
                memory_value,
                confidence,
                conversation_id,
                source_message_id,
                now,
                existing[0],
            ),
        )
        memory_id = existing[0]
        operation = "UPDATED"
    else:
        cursor = connection.execute(
            """
            INSERT INTO memories (
                conversation_id,
                user_id,
                memory_type,
                memory_key,
                memory_value,
                confidence,
                source_message_id,
                created_at,
                updated_at,
                is_active
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 1)
            """,
            (
                conversation_id,
                user_id,
                memory_type,
                memory_key,
                memory_value,
                confidence,
                source_message_id,
                now,
                now,
            ),
        )
        memory_id = cursor.lastrowid
        operation = "CREATED"

    connection.commit()
    connection.close()
    return memory_id, operation


def get_active_memories(user_id):
    """Return active memories for a user."""
    connection = get_connection()
    rows = connection.execute(
        """
        SELECT
            memory_id,
            memory_type,
            memory_key,
            memory_value,
            confidence,
            source_message_id,
            created_at,
            updated_at
        FROM memories
        WHERE user_id = ?
          AND is_active = 1
        ORDER BY memory_id
        """,
        (user_id,),
    ).fetchall()
    connection.close()
    return rows


def deactivate_memory(user_id, memory_key):
    """Deactivate a memory instead of physically deleting it."""
    now = utc_now()
    connection = get_connection()
    cursor = connection.execute(
        """
        UPDATE memories
        SET is_active = 0,
            updated_at = ?
        WHERE user_id = ?
          AND memory_key = ?
          AND is_active = 1
        """,
        (now, user_id, memory_key),
    )
    connection.commit()
    updated = cursor.rowcount
    connection.close()
    return updated


def print_memories(user_id):
    rows = get_active_memories(user_id)

    print("\n" + "=" * 72)
    print("                    STRUCTURED MEMORY")
    print("=" * 72)
    print(f"User: {user_id}")
    print(f"Active memories: {len(rows)}")
    print("-" * 72)

    for row in rows:
        (
            memory_id,
            memory_type,
            memory_key,
            memory_value,
            confidence,
            source_message_id,
            created_at,
            updated_at,
        ) = row

        print(f"Memory ID       : {memory_id}")
        print(f"Type            : {memory_type}")
        print(f"Key             : {memory_key}")
        print(f"Value           : {memory_value}")
        print(f"Confidence      : {confidence}")
        print(f"Source message  : {source_message_id}")
        print(f"Created         : {created_at}")
        print(f"Updated         : {updated_at}")
        print("-" * 72)


def main():
    print("=" * 72)
    print("             STRUCTURED MEMORY - SQLITE TEST")
    print("=" * 72)
    print(f"Database: {DB_PATH}")

    # Step 1: create only the memory table.
    initialize_memory_table()
    print("\n[1] memories table ready.")

    # Step 2: create two test memories derived from our existing conversation.
    # These are manual test records for learning. Later we will automate
    # memory extraction and validation.
    memory_id, operation = upsert_memory(
        user_id=TEST_USER_ID,
        memory_type="preference",
        memory_key="response_style",
        memory_value="Prefers concise technical explanations",
        confidence=0.95,
        conversation_id=TEST_CONVERSATION_ID,
        source_message_id=6,
    )
    print(f"[2] {operation} memory_id={memory_id}: response_style")

    memory_id, operation = upsert_memory(
        user_id=TEST_USER_ID,
        memory_type="goal",
        memory_key="current_goal",
        memory_value="Build an enterprise AI engineering masterclass",
        confidence=0.95,
        conversation_id=TEST_CONVERSATION_ID,
        source_message_id=6,
    )
    print(f"[3] {operation} memory_id={memory_id}: current_goal")

    # Step 3: prove that memory can be retrieved independently from messages.
    print_memories(TEST_USER_ID)

    print("\nMemory flow demonstrated:")
    print("Conversation event")
    print("       ↓")
    print("Memory extraction / decision")
    print("       ↓")
    print("memories table")
    print("       ↓")
    print("Memory retrieval")


if __name__ == "__main__":
    main()
