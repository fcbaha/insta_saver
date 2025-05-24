import os
import logging
import asyncio
import yt_dlp
import requests

from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

# === 🔐 Твой токен от @BotFather ===
BOT_TOKEN = '8068187770:AAFgoNllhfi949EzgyPEz-WDyRk_u6-TGNs'

# === 📝 Настройка логирования ===
logging.basicConfig(filename='bot_errors.log', level=logging.ERROR)


# === ✅ Команда /start ===
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [["/help"]]
    markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text(
        "👋 Здарова! Отправь мне ссылку из Instagram.",
        reply_markup=markup
    )


# === 🆘 Команда /help ===
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📥 Этот бот скачивает видео из Instagram (Reels, посты).\n\n"
        "🔗 Просто отправь мне ссылку, и я пришлю видео.\n"
        "🔒 Приватные аккаунты не поддерживаются.\n"
        "💡 В планах: поддержка TikTok и YouTube."
    )


# === 📦 Обработка ссылок ===
async def handle_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text.strip()

    if "instagram.com" not in url:
        await update.message.reply_text("⚠️ Это не Instagram-ссылка.")
        return

    await update.message.reply_text("⏳ Скачиваю видео...")

    try:
        ydl_opts = {
            'outtmpl': 'insta_video.mp4',
            'format': 'mp4',
            'quiet': True,
            'noplaylist': True,
            'http_headers': {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
                'Accept-Language': 'en-US,en;q=0.9',
            },
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        # Проверка размера
        if os.path.getsize('insta_video.mp4') > 50_000_000:
            os.remove('insta_video.mp4')
            await update.message.reply_text("⚠️ Видео слишком большое (> 50MB). Telegram не может его отправить.")
            return

        # Отправка
        with open('insta_video.mp4', 'rb') as f:
            await update.message.reply_video(f)

        # Задержка и удаление файла
        await asyncio.sleep(2)
        os.remove('insta_video.mp4')

        # Кнопки
        keyboard = [["/help"]]
        markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        await update.message.reply_text("✅ Готово! Хочешь скачать ещё одно видео?", reply_markup=markup)

    except Exception as e:
        logging.error(str(e))
        error_text = str(e)

        if "login" in error_text.lower() or "logged-in users" in error_text:
            await update.message.reply_text("🔒 Это видео доступно только из закрытого аккаунта. Я не могу его скачать.")
        else:
            await update.message.reply_text(f"❌ Ошибка: {e}")


# === 🚀 Запуск бота ===
app = ApplicationBuilder().token(BOT_TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("help", help_command))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_link))

app.run_polling()
