import os
import logging
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, MessageHandler,
    CallbackQueryHandler, filters, ContextTypes
)
import database as db

# بارگذاری توکن از فایل .env
load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")

# تنظیم لاگ
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """دستور /start"""
    await update.message.reply_text(
        "سلام! 👋\n\n"
        "من ربات یادآور کارها هستم.\n\n"
        "📝 برای اضافه کردن کار، فقط متنش رو بنویس و بفرست.\n"
        "📋 برای دیدن کارها: /list\n"
        "❓ برای راهنما: /help"
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """دستور /help"""
    await update.message.reply_text(
        "راهنمای استفاده:\n\n"
        "➕ اضافه کردن کار: فقط متن رو بفرست\n"
        "📋 دیدن لیست: /list\n"
        "🗑 حذف همه کارها: /clear\n"
        "❓ راهنما: /help"
    )


async def list_tasks(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """نمایش لیست کارها"""
    user_id = update.effective_user.id
    tasks = db.get_tasks(user_id)

    if not tasks:
        await update.message.reply_text("📭 هنوز هیچ کاری اضافه نکردی!\n\nفقط متن بفرست تا اضافه کنم.")
        return

    text = "📋 <b>لیست کارهای تو:</b>\n\n"
    keyboard = []

    for task_id, title, done in tasks:
        status = "✅" if done else "⬜"
        text += f"{status} {title}\n"
        keyboard.append([
            InlineKeyboardButton(
                f"{status} {title[:25]}",
                callback_data=f"toggle_{task_id}"
            ),
            InlineKeyboardButton(
                "🗑",
                callback_data=f"delete_{task_id}"
            )
        ])

    await update.message.reply_text(
        text,
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


async def add_task(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """اضافه کردن کار جدید از پیام کاربر"""
    user_id = update.effective_user.id
    title = update.message.text.strip()

    if len(title) > 200:
        await update.message.reply_text("⚠️ متن خیلی طولانیه! حداکثر ۲۰۰ کاراکتر.")
        return

    task_id = db.add_task(user_id, title)
    await update.message.reply_text(
        f"✅ کار اضافه شد!\n\n📝 <b>{title}</b>\n🆔 شناسه: {task_id}",
        parse_mode="HTML"
    )


async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """مدیریت دکمه‌های شیشه‌ای"""
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    data = query.data

    if data.startswith("toggle_"):
        task_id = int(data.split("_")[1])
        db.toggle_task(user_id, task_id)
        await query.message.reply_text(f"✅ وضعیت کار {task_id} تغییر کرد. /list")

    elif data.startswith("delete_"):
        task_id = int(data.split("_")[1])
        db.delete_task(user_id, task_id)
        await query.message.reply_text(f"🗑 کار {task_id} حذف شد.")


async def clear_tasks(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """حذف همه کارها"""
    user_id = update.effective_user.id
    tasks = db.get_tasks(user_id)
    for task_id, _, _ in tasks:
        db.delete_task(user_id, task_id)
    await update.message.reply_text("🗑 همه کارها حذف شدند!")


def main():
    """شروع ربات"""
    db.init_db()

    if not TOKEN:
        print("❌ خطا: توکن ربات پیدا نشد! فایل .env رو چک کن.")
        return

    app = Application.builder().token(TOKEN).build()

    # دستورات
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("list", list_tasks))
    app.add_handler(CommandHandler("clear", clear_tasks))

    # دکمه‌های شیشه‌ای
    app.add_handler(CallbackQueryHandler(button_handler))

    # پیام‌های متنی (اضافه کردن کار)
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, add_task))

    print("🤖 ربات روشن شد! برای خروج Ctrl+C بزن.")
    app.run_polling()


if __name__ == "__main__":
    main()
