# 🤖 Telegram Todo Bot

[![Tests](https://github.com/yasinsaffayy-max/telegram-todo-bot/actions/workflows/tests.yml/badge.svg)](https://github.com/yasinsaffayy-max/telegram-todo-bot/actions)
![Coverage](https://img.shields.io/badge/coverage-95%25-brightgreen)
![Python](https://img.shields.io/badge/python-3.10%2B-blue)
![Telegram](https://img.shields.io/badge/telegram-bot-26A5E4?logo=telegram)
![License](https://img.shields.io/badge/license-MIT-green)

ربات تلگرام مدیریت کارها با پایتون و SQLite

## ✨ امکانات

- ➕ افزودن کار با ارسال متن
- 📋 نمایش لیست کارها با دکمه‌های inline
- ✅ علامت زدن به عنوان انجام‌شده
- 🗑 حذف کارها
- 🧹 پاک کردن همه کارها با /clear
- 🗄 ذخیره‌سازی دائمی در SQLite
- 🧪 ۳۲ تست خودکار با pytest (۹۵٪ coverage)
- ⚙️ CI/CD با GitHub Actions

## 🛠 تکنولوژی‌ها

- Python 3.10+
- python-telegram-bot
- SQLite
- pytest

## 🚀 اجرا

```bash
# 1. نصب پکیج‌ها
pip install -r requirements.txt

# 2. ساخت فایل .env
echo "BOT_TOKEN=توکن_رباتت_رو_اینجا_بذار" > .env

# 3. اجرا
python bot.py
```

🎯 دستورات ربات

دستور کار
/start شروع
/help راهنما
/list نمایش لیست کارها
/clear حذف همه کارها
(ارسال متن) افزودن کار جدید

🧪 تست

```bash
pytest --cov=. --cov-report=term-missing
```

📁 ساختار پروژه

```
telegram-todo-bot/
├── bot.py              # منطق ربات
├── database.py         # توابع دیتابیس
├── tests/
│   ├── conftest.py
│   ├── test_bot.py
│   └── test_database.py
├── .github/workflows/  # CI
├── pytest.ini
├── requirements.txt
└── README.md
```

📝 لایسنس

MIT
