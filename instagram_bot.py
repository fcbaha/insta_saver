import os
import logging
import random
import requests
from flask import Flask
from threading import Thread
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
import yt_dlp

# Telegram token
BOT_TOKEN = os.environ.get("BOT_TOKEN")

# Instagram cookies (не меняй, если не истекли)
COOKIES_STRING = (
    "mid=Z-JcogALAAHBuU_jpo2DmCqHCKqB; "
    "datr=olziZyt4Xj82VkHmV3nmGF12; "
    "ig_did=A1F5CBE3-F0C5-4468-875E-E5415F9A1EE9; "
    "ig_nrcb=1; "
    "csrftoken=ONFysLggevyniNoB0MYrIJpBnyZ1JxFi; "
    "ds_user_id=48658772952; "
    "wd=1536x703; "
    "dpr=1.25; "
    "ps_l=1; "
    "ps_n=1; "
    "sessionid=48658772952%3AmOjL1NHJJqKhQD%3A1%3AAYfz_-8oerdCknZnwLAi6bfNLaLx0wTDTGVuzqlnBg; "
    "rur=\"CLN\\05448658772952\\0541781283030:01fe1e976d3a3b16d07ea873e605cd27a8228d699f815235f9aae8937a55ecf313e4fc70\""
)

logging.basicConfig(filename='bot_errors.log', level=logging.ERROR)

before_download = [
    "📥 Высасываю твой Reels, как последний сок из трубочки...",
    "🔄 Конвертирую твой запрос в MP4, как настоящий гений...",
    "⌛ Жди, пока инстаграм выдаст мне твой контент через боль...",
    "🚀 Запускаю ракету, чтобы быстрее скачать..."
]

after_download = [
    "Вот твой видос 😏",
    "Инстаграм дрожит от твоих запросов... держи 👀",
    "Снова Reels? Да ты гуру скроллинга! 🏆",
    "Лови, пока инста не передумала! 🎁"
]

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Привет! Отправь ссылку из Instagram — и я скачаю Reels или пост-видео!",
        reply_markup=ReplyKeyboardMarkup([["/help"]], resize_keyboard=True)
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📥 Просто пришли ссылку на Reels из Instagram — и я скачаю его для тебя!"
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message.text.strip()

    if "instagram.com" in message:
        await update.message.reply_text(random.choice(before_download))
        try:
            ydl_opts = {
                'outtmpl': 'insta_video.mp4',
                'format': 'mp4',
                'quiet': True,
                'noplaylist': True,
                'http_headers': {
                    'User-Agent': 'Mozilla/5.0',
                    'Accept-Language': 'en-US,en;q=0.9',
                    'Cookie': COOKIES_STRING
                }
            }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([message])

            if os.path.getsize("insta_video.mp4") > 50_000_000:
                os.remove("insta_video.mp4")
                await update.message.reply_text("⚠️ Видео слишком большое для Telegram (>50MB).")
                return

            with open("insta_video.mp4", "rb") as f:
                await update.message.reply_video(f)

            os.remove("insta_video.mp4")
            await update.message.reply_text(random.choice(after_download))
        except Exception as e:
            logging.error(str(e))
            await update.message.reply_text("❌ Не удалось скачать видео. Проверь ссылку или попробуй позже.")
    else:
        await update.message.reply_text("❗ Это не похоже на Instagram-ссылку. Попробуй снова.")

# Flask-сервер для Render
flask_app = Flask(__name__)

@flask_app.route('/')
def home():
    return "✅ Бот активен!"

def run_flask():
    flask_app.run(host="0.0.0.0", port=8000)

def run_bot():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.run_polling()

if __name__ == '__main__':
    Thread(target=run_flask, daemon=True).start()
    run_bot()
