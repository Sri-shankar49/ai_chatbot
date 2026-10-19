
import sqlite3
import uuid
import json
from datetime import datetime, timezone
from pathlib import Path

# from config.settings import BACKEND_DIR
from config.settings import BACKEND_DIR, CHAT_DB_PATH

# DB_PATH = BACKEND_DIR / "chat_history.db"
configured_db_path = Path(CHAT_DB_PATH)

DB_PATH = (
    configured_db_path
    if configured_db_path.is_absolute()
    else BACKEND_DIR / configured_db_path
)


def get_connection():
    connection = sqlite3.connect(DB_PATH, timeout=10)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def init_db():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)

    with get_connection() as connection:
        connection.executescript(
            """
            CREATE TABLE IF NOT EXISTS conversations (
                id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS messages (
                id TEXT PRIMARY KEY,
                conversation_id TEXT NOT NULL,
                role TEXT NOT NULL
                    CHECK(role IN ('user', 'assistant')),
                content TEXT NOT NULL,
                created_at TEXT NOT NULL,
                FOREIGN KEY(conversation_id)
                    REFERENCES conversations(id)
                    ON DELETE CASCADE
            );

            CREATE INDEX IF NOT EXISTS
                idx_messages_conversation
            ON messages(conversation_id, created_at);
            """
        )
        
    columns = connection.execute("PRAGMA table_info(messages)").fetchall()
            
    column_names = {column["name"] for column in columns}
            
    if "sources" not in column_names:
        connection.execute(
            "ALTER TABLE messages ADD COLUMN sources TEXT"
        )


def create_conversation(title: str = "New conversation") -> dict:
    conversation_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc).isoformat()

    with get_connection() as connection:
        connection.execute(
            """
            INSERT INTO conversations
                (id, title, created_at, updated_at)
            VALUES (?, ?, ?, ?)
            """,
            (conversation_id, title, now, now),
        )

    return {
        "id": conversation_id,
        "title": title,
        "created_at": now,
        "updated_at": now,
    }


def add_message(
    conversation_id: str,
    role: str,
    content: str,
    sources: list[dict] | None = None,
) -> dict:
    if role not in {"user", "assistant"}:
        raise ValueError("Invalid message role.")

    message_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc).isoformat()
    sources_json = json.dumps(sources or [])

    with get_connection() as connection:
        conversation = connection.execute(
            "SELECT id, title FROM conversations WHERE id = ?",
            (conversation_id,),
        ).fetchone()

        if conversation is None:
            raise ValueError("Conversation not found.")

        connection.execute(
            """
            INSERT INTO messages
                (id, conversation_id, role, content, created_at,sources)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (message_id, conversation_id, role, content, now, sources_json),
        )

        title = conversation["title"]
        if title == "New conversation" and role == "user":
            title = content[:60] or "New conversation"

        connection.execute(
            """
            UPDATE conversations
            SET title = ?, updated_at = ?
            WHERE id = ?
            """,
            (title, now, conversation_id),
        )

    return {
        "id": message_id,
        "conversation_id": conversation_id,
        "role": role,
        "content": content,
        "created_at": now,
    }


# def get_messages(
#     conversation_id: str,
#     limit: int = 20,
# ) -> list[dict]:
#     with get_connection() as connection:
#         rows = connection.execute(
#             """
#             SELECT id, conversation_id, role, content, created_at
#             FROM messages
#             WHERE conversation_id = ?
#             ORDER BY created_at DESC, id DESC
#             LIMIT ?
#             """,
#             (conversation_id, limit),
#         ).fetchall()
        
#     # return [dict(row) for row in rows]

#     # Reverse the newest-first results for chronological chat history.
#     return [dict(row) for row in reversed(rows)]

def get_messages(
    conversation_id: str,
    limit: int = 20,
) -> list[dict]:
    with get_connection() as connection:
        rows = connection.execute(
            """
            SELECT
                id,
                conversation_id,
                role,
                content,
                created_at,
                sources
            FROM messages
            WHERE conversation_id = ?
            ORDER BY created_at DESC, id DESC
            LIMIT ?
            """,
            (conversation_id, limit),
        ).fetchall()

    messages = []

    for row in reversed(rows):
        message = dict(row)

        try:
            message["sources"] = json.loads(
                message.get("sources") or "[]"
            )
        except (json.JSONDecodeError, TypeError):
            message["sources"] = []

        messages.append(message)

    return messages


def list_conversations() -> list[dict]:
    with get_connection() as connection:
        rows = connection.execute(
            """
            SELECT
                c.id,
                c.title,
                c.created_at,
                c.updated_at,
                COUNT(m.id) AS message_count
            FROM conversations c
            LEFT JOIN messages m ON m.conversation_id = c.id
            GROUP BY c.id
            ORDER BY c.updated_at DESC
            """
        ).fetchall()

    return [dict(row) for row in rows]
