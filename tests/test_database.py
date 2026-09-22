import database as db


class TestInitDb:
    def test_init_creates_table(self, temp_db):
        """جدول باید ساخته بشه"""
        import sqlite3
        conn = sqlite3.connect(temp_db)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='tasks'")
        assert cursor.fetchone() is not None
        conn.close()

    def test_init_twice_safe(self, temp_db):
        """دو بار init نباید خطا بده"""
        db.init_db()
        db.init_db()


class TestAddTask:
    def test_add_returns_id(self, temp_db):
        task_id = db.add_task(12345, "خرید نان")
        assert task_id == 1

    def test_add_increments_id(self, temp_db):
        id1 = db.add_task(12345, "تسک اول")
        id2 = db.add_task(12345, "تسک دوم")
        assert id2 == id1 + 1

    def test_add_multiple(self, temp_db):
        for i in range(5):
            db.add_task(12345, f"تسک {i}")
        tasks = db.get_tasks(12345)
        assert len(tasks) == 5

    def test_add_different_users(self, temp_db):
        db.add_task(111, "مال یوزر ۱")
        db.add_task(222, "مال یوزر ۲")
        assert len(db.get_tasks(111)) == 1
        assert len(db.get_tasks(222)) == 1


class TestGetTasks:
    def test_empty(self, temp_db):
        assert db.get_tasks(99999) == []

    def test_only_user_tasks(self, temp_db):
        db.add_task(111, "a")
        db.add_task(222, "b")
        db.add_task(111, "c")
        tasks = db.get_tasks(111)
        assert len(tasks) == 2
        titles = [t[1] for t in tasks]
        assert "a" in titles
        assert "c" in titles
        assert "b" not in titles

    def test_returns_tuple_format(self, temp_db):
        db.add_task(12345, "تست")
        tasks = db.get_tasks(12345)
        assert len(tasks[0]) == 3  # (id, title, done)
        assert tasks[0][1] == "تست"
        assert tasks[0][2] == 0

    def test_ordered_newest_first(self, temp_db):
        db.add_task(12345, "اول")
        db.add_task(12345, "دوم")
        db.add_task(12345, "سوم")
        tasks = db.get_tasks(12345)
        assert tasks[0][1] == "سوم"  # آخری اول


class TestToggleTask:
    def test_toggle_done(self, temp_db):
        tid = db.add_task(12345, "تست")
        db.toggle_task(12345, tid)
        tasks = db.get_tasks(12345)
        assert tasks[0][2] == 1  # done

    def test_toggle_twice(self, temp_db):
        tid = db.add_task(12345, "تست")
        db.toggle_task(12345, tid)
        db.toggle_task(12345, tid)
        tasks = db.get_tasks(12345)
        assert tasks[0][2] == 0  # برگشت

    def test_toggle_wrong_user(self, temp_db):
        tid = db.add_task(111, "تست")
        db.toggle_task(999, tid)  # یوزر اشتباه
        tasks = db.get_tasks(111)
        assert tasks[0][2] == 0  # تغییر نکرد

    def test_toggle_nonexistent(self, temp_db):
        db.toggle_task(12345, 99999)  # نباید خطا بده


class TestDeleteTask:
    def test_delete(self, temp_db):
        tid = db.add_task(12345, "تست")
        db.delete_task(12345, tid)
        assert db.get_tasks(12345) == []

    def test_delete_wrong_user(self, temp_db):
        tid = db.add_task(111, "تست")
        db.delete_task(999, tid)
        assert len(db.get_tasks(111)) == 1

    def test_delete_nonexistent(self, temp_db):
        db.delete_task(12345, 99999)  # نباید خطا

    def test_delete_one_of_many(self, temp_db):
        id1 = db.add_task(12345, "a")
        db.add_task(12345, "b")
        db.add_task(12345, "c")
        db.delete_task(12345, id1)
        assert len(db.get_tasks(12345)) == 2
