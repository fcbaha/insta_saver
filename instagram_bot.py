import os
import logging
import random
import requests
from flask import Flask
from threading import Thread
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
import yt_dlp
import asyncio

BOT_TOKEN = os.environ.get("BOT_TOKEN")
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")  # Добавь эту переменную в Render
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"

COOKIES_STRING = "..."  # обрежем для читаемости

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
    await update.message.reply_text("👋 Привет! Отправь ссылку из Instagram или просто задай вопрос!", reply_markup=ReplyKeyboardMarkup([["/help"]], resize_keyboard=True))

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📥 Отправь ссылку на пост или Reels из Instagram, или напиши мне что-нибудь — я попробую ответить умно ✨")

async def ask_groq(prompt: str) -> str:
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "mixtral-8x7b-32768",
        "messages": [
            {"role": "system", "content": "Ты дружелюбный Telegram-бот."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.7
    }
    try:
        response = requests.post(GROQ_URL, headers=headers, json=data, timeout=30)
        response.raise_for_status()
        reply = response.json()['choices'][0]['message']['content']
        return reply.strip()
    except Exception as e:
        logging.error(f"Groq API error: {str(e)}")
        return "❌ Извини, я не смог получить ответ. Попробуй позже."

async def handle_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text.strip()
    user_id = update.message.from_user.id

    if "instagram.com" in url:
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
                ydl.download([url])

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
        reply = await ask_groq(url)
        await update.message.reply_text(reply)

flask_app = Flask(__name__)

@flask_app.route('/')
def home():
    return "✅ Бот активен и работает!"

def run_flask():
    flask_app.run(host="0.0.0.0", port=8000)

def run():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_link))
    app.run_polling()

if __name__ == '__main__':
    Thread(target=run_flask, daemon=True).start()
    run()
