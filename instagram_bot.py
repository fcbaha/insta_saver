import os
import logging
import random
from flask import Flask
from threading import Thread
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
import yt_dlp
import asyncio

BOT_TOKEN = os.environ.get("BOT_TOKEN")



COOKIES_STRING = (
    "mid=Z-JcogALAAHBuU_jpo2DmCqHCKqB; "
    "datr=olziZyt4Xj82VkHmV3nmGF12; "
    "ig_did=A1F5CBE3-F0C5-4468-875E-E5415F9A1EE9; "
    "ig_nrcb=1; wd=1536x703; dpr=1.25; "
    "csrftoken=ONFysLggevyniNoB0MYrIJpBnyZ1JxFi; "
    "ds_user_id=48658772952; "
    "sessionid=48658772952%3AmOjL1NHJJqKhQD%3A1%3AAYd3dkzxBIdtR4lyhwufcOitx374P6dKNIXjBNnfvA; "
    "rur=RVA\05448658772952\0541779899514:01f7acbdb41a99e31f0fe7fec4eab2e290f5268bef2be7cb15b1128f687336341985b051"
)

logging.basicConfig(filename='bot_errors.log', level=logging.ERROR)

user_links_count = {}

before_download = [
    "📥 Высасываю твой Reels, как последний сок из трубочки...",
"🔄 Конвертирую твой запрос в кривое MP4, как настоящий гений...",
"⌛ Жди, пока инстаграм выдаст мне твой контент через боль...",
"🤖 Мои сервера стонут, но терпят ради твоего мема...",
"💾 Сохраняю видео, а заодно и твои грехи в историю...",
"🔥 Прожигаю дыру в интернете ради твоего Reels...",
"⚡ Ускоряю загрузку силой чистой ненависти...",
"💀 Если это не скачается, я официально сдаюсь...",
"🖕 Держи, но знай — ты меня изрядно достал...",
"🤡 Готовлю твой контент с любовью (но это не точно)...",
"🐌 Загружаю со скоростью улитки в спящем режиме...",
"🧊 Сервера инсты сегодня холодные, как твое сердце...",
"🦥 Жди, пока обезьяна с ноутбуком закончит работу...",
"💩 Конвертация прошла успешно (но качество — как у Nokia 3310)...",
"🚀 Хотел сделать быстро, но инстаграм — не космос...",
"🕵️‍♂️ Воруем твой контент при свете дня (шутка... или нет)",
"🎬 Твой Reels уже почти в топе (топа моих страданий)...",
"🤏 Щя 10 сек получишь свое тупое-видео...",
"👾 Взламываю матрицу... или просто жду загрузки",
"🍿 Попкорн готов, а твое видео — почти..."
]

after_download = [
    "Ну чё, опять свою дичь качаем? Держи, кретин,",
"Опа, ещё один шедевр для твоей коллекции говна,",
"Серьёзно? Это вот прямо вот реально нужно было качать? Ну ок,",
"Вот твой видос, наслаждайся своим мусором,",
"Опять? Да ты, бля, конченый! Ладно, держи,",
"Ну чё, дебил, скачал - теперь иди вешай это в свой тг-канал,",
"Бля, ну сколько можно? Вот, возьми и отъебись,",
"Ты реально думаешь этот клип что-то изменит в твоей жизни? Ну ок,",
"Лови, чёрт. Но если это опять котики - я тебя найду,",
"О, да это же твой 228-й бесполезный релс! Ты упорный, как таракан,",
"Готово. Теперь иди нахуй, хорошего дня,",
"Опять инста? Да у тебя, сука, зависимость,",
"Ну чё, снова хуйню какую-то качаешь? На, дегенерат,",
"Очередной видос для твоего деградационного марафона! Жги,",
"Серьёзно? Ещё один релс? Да ты скроллозавр,",
"Вот твоё говно... ой, то есть 'контент'. Держи,",
"Опять? Сука, да ты заебал! Ладно, лови,",
"Ну чё, дебил, скачал - теперь иди спамь это везде,",
"Бля, ну хватит уже! Вот твой видос, отвали,",
"Ты реально думаешь этот уёбищный клип стоит моего времени? Держи,",
"Лови, мудила. Но если это опять танцы - я в баню,",
"О, да это же твой 300-й релс! Ты, блять, монстр,",
"Готово. Теперь иди нахуй и не беспокой 5 минут,",
"Опять инста? Да ты, сука, как наркоман,",
"Ну чё, снова какую-то дичь качаем? На, идиот,",
"Опа, очередной шедевр для твоей помойки! Наслаждайся,",
"Серьёзно? Это вот прямо вот реально нужно было? Ну окей,",
"Вот твой 'контент'. Выглядит как мусор, но тебе нравится,",
"Опять? Да ты, бля, безбашенный! Ладно, держи,",
"Ну чё, дегенерат, скачал - теперь иди вешай куда хочешь,",
"Бля, ну сколько можно? Вот, возьми и отъебись на полчаса,",
"Ты реально думаешь этот клип что-то изменит? Ну держи,",
"Лови, кретин. Но если это опять котики - я в ахуе,",
"О, да это же твой 500-й релс! Ты, блять, машина,",
"Готово. Теперь иди нахуй, хорошего вечера,",
"Опять инста? Да ты, сука, как робот,",
"Ну чё, опять свою хуйню качаем? На, мудак,",
"Очередной видос для твоей коллекции цифрового мусора! Жги,",
"Серьёзно? Ещё один? Да ты скролломаньяк,",
"Вот твоё говно... ой, 'видео'. Держи,",
"Опять? Сука, да ты спамер! Ладно, лови,",
"Ну чё, идиот, скачал - теперь иди спамь,",
"Бля, ну хватит! Вот твой видос, отъебись,",
"Ты реально думаешь этот клип стоит времени? Ну ок,",
"Лови, дебил. Но если это опять мемы - я в шоке,",
"О, да это же твой 1000-й релс! Ты легенда,",
"Готово. Теперь иди нахуй, приятного просмотра,",
"Опять инста? Да ты, сука, как зомби,",
"Ну чё, снова какую-то дичь качаем? На, долбаёб,",
"Последний раз качаю, блядь! (шучу, кидай ещё),",
"С такой коллекцией рилсов ты можешь преподавать бесполезность,",
"С такой скоростью ты скоро обгонишь Флэша… по бесполезному контенту,",
"Даже Гендальф сказал бы: 'Ты не пройдёшь!' — мимо нормального контента,",
"Память телефона страдает больше, чем Ваканда после финала,",
"Каждый раз, когда ты качаешь рилс, где-то плачет один Тони Старк,",
"Ты не избранный, Нео, ты просто залипаешь в обёртку от матрицы,",
"Когда ты смотришь рилсы — даже Властелин Колец кажется коротким,",
"Мстители собрались, чтобы спасти планету. А ты — чтобы скачать танец из TikTok,",
"Если бы бесполезный контент был суперсилой — ты был бы Бэтмен без костюма и денег,",
"Ты открыл портал. Но не в мультивселенную, а в кринж-безумие,",
"Один ты способен потратить 30 ГБ на мемы и остаться довольным,",
"Если бы лень была персонажем — она бы выглядела точно как твоя галерея,",
"Знаешь, кто тоже думал, что всё под контролем? Титаник,",
"Твоё чувство вкуса — как сюжет у Форсажа после 5-й части,",
"Этот клип — прям как новый сезон 'Ведьмака': никто не просил, но вот он,",
"Ты качаешь так, будто завтра интернет отключат навсегда,",
"В тебе столько пользы, сколько в сценах после титров у неудавшихся фильмов,",
"Даже Дарта Вейдера бы задушило от количества кринжа в твоём телефоне,",
"Ты — ходячий пролог к фильму, который никто не собирается смотреть,",
"Скорость скачивания у тебя как у Флэша, а смысл — как у Патрика из 'Спанч Боба',",
"Каждое твоё действие в интернете — это удалённая сцена из 'Дурнушки Бетти',",
"Если бы интеллект оценивали по галерее, ты бы не прошёл кастинг даже в 'Дом-2',",
"Этот видос тебя не спасёт, как и сцена, вырезанная из 'Звёздных войн',",
"Ты тратишь время, как Джокер тратит бензин — красиво, но с огнём и без цели,",
"Ты — как третий сезон любого сериала Netflix: вроде есть, но лучше бы не было,",
"Каждый твой выбор — как поворот в фильмах Шьямалана: странно и без логики,",
"Ты думаешь, что качаешь легендарное. Спойлер: нет,",
"Даже Стрэндж бы не смог увидеть таймлайн, где ты используешь клип по делу,",
"Ты бы идеально вписался в фон 'Игры престолов' — где всё красиво, но всем плевать,",
"Этот файл не изменит твою жизнь, как и 73 предыдущих,",
"Если бы видео были делом жизни, ты бы уже получил Оскар за бессмысленность,",
"Уровень деградации: смотришь мемы и думаешь, что учишься жизни,",
"Ты качаешь так, будто где-то за это дают бонусы в аду,",
"Ник Фьюри бы даже не стал тебя вербовать в команду, только забанил,",
"Ты — это ошибка в сценарии Marvel, которую забыли вырезать,",
"Если бы телефон умел говорить, он бы подал в суд за насилие мемами,",
"Этот файл — как Джар-Джар Бинкс: даже фанаты не хотят его видеть,",
"Ты — как фон в 'Очень странных делах': шумный, странный и никому не нужный,",
"Тебя даже в 'Чёрном зеркале' показали бы как 'вот так делать не надо',",
"Ты качаешь видео с такой страстью, будто пытаешься вызвать Ктулху,",
"Если бы был сериал 'Как всё испортить' — ты был бы пилотной серией,",
]

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 Привет! Отправь ссылку из Instagram.", reply_markup=ReplyKeyboardMarkup([["/help"]], resize_keyboard=True))

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📥 Отправь ссылку на пост или Reels из Instagram, и я скачаю видео для тебя.")

async def handle_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text.strip()
    user_id = update.message.from_user.id

    if "instagram.com" not in url:
        await update.message.reply_text("⚠️ Это не Instagram-ссылка.")
        return

    ##user_links_count[user_id] = user_links_count.get(user_id, 0) + 1
    ##if user_links_count[user_id] >= 5:
        ##await update.message.reply_text("🧠 Бро, отдохни от Instagram на пару минут 😄")
        ##return

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
