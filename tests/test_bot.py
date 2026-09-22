import pytest
from unittest.mock import AsyncMock, MagicMock, patch
import bot as bot_module
import database as db


@pytest.fixture
def mock_update():
    """یه Update شبیه‌سازی شده"""
    update = MagicMock()
    update.effective_user.id = 12345
    update.message.text = "خرید نان"
    update.message.reply_text = AsyncMock()
    return update


@pytest.fixture
def mock_context():
    return MagicMock()


class TestStartCommand:
    async def test_start_sends_message(self, mock_update, mock_context):
        await bot_module.start(mock_update, mock_context)
        mock_update.message.reply_text.assert_called_once()
        call_args = mock_update.message.reply_text.call_args[0][0]
        assert "سلام" in call_args
        assert "/list" in call_args


class TestHelpCommand:
    async def test_help_sends_help(self, mock_update, mock_context):
        await bot_module.help_command(mock_update, mock_context)
        mock_update.message.reply_text.assert_called_once()
        call_args = mock_update.message.reply_text.call_args[0][0]
        assert "/list" in call_args
        assert "/clear" in call_args


class TestAddTask:
    async def test_add_valid_task(self, mock_update, mock_context, temp_db):
        mock_update.message.text = "خرید شیر"
        await bot_module.add_task(mock_update, mock_context)
        # باید توی DB ذخیره شده باشه
        tasks = db.get_tasks(12345)
        assert len(tasks) == 1
        assert tasks[0][1] == "خرید شیر"

    async def test_add_too_long_task(self, mock_update, mock_context, temp_db):
        mock_update.message.text = "a" * 201
        await bot_module.add_task(mock_update, mock_context)
        # نباید ذخیره بشه
        assert len(db.get_tasks(12345)) == 0
        # باید پیام خطا داده باشه
        call_args = mock_update.message.reply_text.call_args[0][0]
        assert "طولانی" in call_args

    async def test_add_200_char_task(self, mock_update, mock_context, temp_db):
        mock_update.message.text = "a" * 200
        await bot_module.add_task(mock_update, mock_context)
        # دقیقاً ۲۰۰ کاراکتر مجازه
        assert len(db.get_tasks(12345)) == 1


class TestListTasks:
    async def test_list_empty(self, mock_update, mock_context, temp_db):
        await bot_module.list_tasks(mock_update, mock_context)
        call_args = mock_update.message.reply_text.call_args[0][0]
        assert "هنوز" in call_args or "خالی" in call_args

    async def test_list_with_tasks(self, mock_update, mock_context, temp_db):
        db.add_task(12345, "خرید نان")
        db.add_task(12345, "خواندن کتاب")
        await bot_module.list_tasks(mock_update, mock_context)
        mock_update.message.reply_text.assert_called_once()

    async def test_list_only_user_tasks(self, mock_update, mock_context, temp_db):
        db.add_task(12345, "مال من")
        db.add_task(99999, "مال یکی دیگه")
        await bot_module.list_tasks(mock_update, mock_context)
        call_args = mock_update.message.reply_text.call_args
        text = call_args[0][0]
        assert "مال من" in text
        assert "مال یکی دیگه" not in text


class TestClearTasks:
    async def test_clear_removes_all(self, mock_update, mock_context, temp_db):
        db.add_task(12345, "a")
        db.add_task(12345, "b")
        db.add_task(12345, "c")
        await bot_module.clear_tasks(mock_update, mock_context)
        assert len(db.get_tasks(12345)) == 0

    async def test_clear_only_user_tasks(self, mock_update, mock_context, temp_db):
        db.add_task(12345, "مال من")
        db.add_task(99999, "مال یکی دیگه")
        await bot_module.clear_tasks(mock_update, mock_context)
        assert len(db.get_tasks(12345)) == 0
        assert len(db.get_tasks(99999)) == 1


@pytest.fixture
def mock_callback_update():
    """یه Update با callback_query شبیه‌سازی شده"""
    update = MagicMock()
    update.callback_query = MagicMock()
    update.callback_query.from_user.id = 12345
    update.callback_query.answer = AsyncMock()
    update.callback_query.message.reply_text = AsyncMock()
    return update


class TestButtonHandler:
    async def test_toggle_button(self, mock_callback_update, mock_context, temp_db):
        tid = db.add_task(12345, "تست")
        mock_callback_update.callback_query.data = f"toggle_{tid}"
        await bot_module.button_handler(mock_callback_update, mock_context)
        # باید toggle شده باشه
        tasks = db.get_tasks(12345)
        assert tasks[0][2] == 1
        mock_callback_update.callback_query.answer.assert_called_once()

    async def test_delete_button(self, mock_callback_update, mock_context, temp_db):
        tid = db.add_task(12345, "تست")
        mock_callback_update.callback_query.data = f"delete_{tid}"
        await bot_module.button_handler(mock_callback_update, mock_context)
        # باید حذف شده باشه
        assert len(db.get_tasks(12345)) == 0

    async def test_delete_nonexistent(self, mock_callback_update, mock_context, temp_db):
        mock_callback_update.callback_query.data = "delete_99999"
        await bot_module.button_handler(mock_callback_update, mock_context)
        # نباید خطا بده

    async def test_toggle_wrong_user(self, mock_callback_update, mock_context, temp_db):
        tid = db.add_task(99999, "مال یکی دیگه")
        mock_callback_update.callback_query.from_user.id = 12345
        mock_callback_update.callback_query.data = f"toggle_{tid}"
        await bot_module.button_handler(mock_callback_update, mock_context)
        # نباید تغییر کنه
        tasks = db.get_tasks(99999)
        assert tasks[0][2] == 0
