import os
import tempfile
import pytest
import database as db


@pytest.fixture(autouse=True)
def temp_db(monkeypatch):
    """برای هر تست، یه دیتابیس موقت جدا می‌سازه"""
    fd, path = tempfile.mkstemp(suffix='.db')
    os.close(fd)
    monkeypatch.setenv('DB_NAME', path)
    db.init_db()
    yield path
    try:
        os.unlink(path)
    except OSError:
        pass
