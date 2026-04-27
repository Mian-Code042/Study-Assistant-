import sqlite3
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional

DB_PATH = Path("study_assistant.db")

def init_db():
    """Initialize database with improved schema"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Documents Table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS documents (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        filename TEXT UNIQUE,
        file_path TEXT,
        chunks INTEGER,
        uploaded_at TEXT DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    # History / Interactions Table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        document_id INTEGER,
        interaction_type TEXT,     -- 'chat', 'mcqs', 'flashcards'
        topic TEXT,
        question TEXT,
        content TEXT,              -- answer / mcqs / flashcards
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (document_id) REFERENCES documents(id)
    )
    ''')

    conn.commit()
    conn.close()
    print("✅ SQLite Database initialized successfully!")


def save_document(filename: str, file_path: str, chunks: int) -> int:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT OR REPLACE INTO documents (filename, file_path, chunks)
        VALUES (?, ?, ?)
    ''', (filename, str(file_path), chunks))
    doc_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return doc_id


def save_history(document_id: Optional[int], interaction_type: str, topic: str, 
                 question: str, content: str):
    """Save chat, mcqs or flashcards"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO history 
        (document_id, interaction_type, topic, question, content, created_at)
        VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
    ''', (document_id, interaction_type, topic, question, content))
    conn.commit()
    conn.close()


def clear_history() -> int:
    """Delete all history rows and return removed count."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) FROM history')
    total = cursor.fetchone()[0]
    cursor.execute('DELETE FROM history')
    conn.commit()
    conn.close()
    return total


def search_history(query: str, limit: int = 20) -> List[Dict]:
    """Search in history (question + content + topic)"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT h.id, d.filename, h.interaction_type, h.topic, 
               h.question, h.content, h.created_at
        FROM history h
        LEFT JOIN documents d ON h.document_id = d.id
        WHERE h.question LIKE ? 
           OR h.content LIKE ? 
           OR h.topic LIKE ?
        ORDER BY h.created_at DESC
        LIMIT ?
    ''', (f'%{query}%', f'%{query}%', f'%{query}%', limit))
    
    rows = cursor.fetchall()
    conn.close()

    return [
        {
            "id": row[0],
            "document": row[1],
            "type": row[2],
            "topic": row[3],
            "question": row[4],
            "content": row[5],
            "timestamp": row[6]
        } for row in rows
    ]


def get_all_history(limit: int = 50) -> List[Dict]:
    """Get all history (for sidebar)"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT h.id, d.filename, h.interaction_type, h.topic, 
               h.question, h.content, h.created_at
        FROM history h
        LEFT JOIN documents d ON h.document_id = d.id
        ORDER BY h.created_at DESC
        LIMIT ?
    ''', (limit,))
    
    rows = cursor.fetchall()
    conn.close()
    return [dict(zip([col[0] for col in cursor.description], row)) for row in rows]