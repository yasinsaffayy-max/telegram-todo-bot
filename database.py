import os
import sqlite3
from datetime import datetime


def get_db_name():
    """مسیر دیتابیس — قابل تغییر با env برای تست"""
    return os.environ.get("DB_NAME", "tasks.db")


def get_connection():
    """اتصال به دیتابیس"""
    return sqlite3.connect(get_db_name())


def init_db():
    """ساخت جدول‌ها در اولین اجرا"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            done INTEGER DEFAULT 0,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()


def add_task(user_id: int, title: str) -> int:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO tasks (user_id, title) VALUES (?, ?)",
        (user_id, title)
    )
    task_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return task_id


def get_tasks(user_id: int):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, title, done FROM tasks WHERE user_id = ? ORDER BY id DESC",
        (user_id,)
    )
    tasks = cursor.fetchall()
    conn.close()
    return tasks


def toggle_task(user_id: int, task_id: int):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE tasks SET done = 1 - done WHERE id = ? AND user_id = ?",
        (task_id, user_id)
    )
    conn.commit()
    conn.close()


def delete_task(user_id: int, task_id: int):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "DELETE FROM tasks WHERE id = ? AND user_id = ?",
        (task_id, user_id)
    )
    conn.commit()
    conn.close()
