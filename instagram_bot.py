import os
import logging
import random
import requests
from flask import Flask
from threading import Thread
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
import yt_dlp

BOT_TOKEN = os.environ.get("BOT_TOKEN")
OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY")

COOKIES_STRING = "your_instagram_cookies_here"  # вставь свои cookies

logging.basicConfig(filename='bot_errors.log', level=logging.ERROR)

before_download = [
    "📥 Высасываю твой Reels, как последний сок из трубочки...",
    "🔄 Конвертирую твой запрос в кривое MP4, как настоящий гений...",
    "⌛ Жди, пока инстаграм выдаст мне твой контент через боль...",
    "🔥 Разогреваю сервера для вашего видео...",
    "🎬 Ваш контент проходит премьерный показ...",
    "⚡ Ускоряю интернет кулаками...",
    "🧙‍♂️ Колдую над ссылкой, почти получилось...",
    "🚀 Запускаю ракету, чтобы быстрее скачать..."
]

after_download = [
    "Вот твой видос, не благодари... хотя ладно, благодари 😏",
"Инстаграм дрожит от твоих запросов... держи 👀",
"Ещё один клик — и ты в моих руках. Ой, то есть вот видео 😈",
"Ты точно не агент ФБР? Ладно, держи, но я слежу за тобой 👁️",
"Снова Reels? Да ты гуру скроллинга! 🏆",
"Видео готово! (А теперь иди работай, а не в соцсетях сиди) 🚀",
"Лови видос, пока инста не передумала! �",
"Ты что, решил скачать весь инстаграм? Ну держи... 😅",
"Опа, ещё один контент-вор... шучу, лови! 🎁",
"Видео добыто! Теперь можешь флексить в чатиках 😎",
"Ты так часто просишь, что скоро я начну брать подписку! 💸",
"Готово! Но если это котики — я уже в доле 🐱"
]

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Привет! Отправь ссылку из Instagram или просто задай вопрос!",
        reply_markup=ReplyKeyboardMarkup([["/help"]], resize_keyboard=True)
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📥 Отправь ссылку на Reels из Instagram, или напиши вопрос — я постараюсь ответить ✨"
    )

async def ask_openrouter(prompt: str) -> str:
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "openchat/openchat-7b:free",
        "messages": [
            {"role": "system", "content": "Ты умный Telegram-бот, отвечай дружелюбно."},
            {"role": "user", "content": prompt}
        ]
    }

    try:
        response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=payload, timeout=30)
        response.raise_for_status()
        return response.json()['choices'][0]['message']['content'].strip()
    except Exception as e:
        logging.error(f"OpenRouter API error: {str(e)}")
        return "❌ Я не смог получить ответ. Попробуй позже."

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
        reply = await ask_openrouter(message)
        await update.message.reply_text(reply)

# Flask для Render
flask_app = Flask(__name__)

@flask_app.route('/')
def home():
    return "✅ Бот работает!"

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
