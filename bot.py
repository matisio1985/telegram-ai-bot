
import sqlite3
from telegram import Update, KeyboardButton, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
import asyncio

BOT_TOKEN = "7805856290:AAG8iYYiGhd2AXEJQ916TtH0SjywXK1rkoQ"
DAILY_HOUR = 10  # 10:00 uur
LINK = "https://phoampor.top/4/9213058"

tips_nl = [
    "Gebruik Copy.ai om automatisch blogs en social media posts te genereren.",
    "Verwijder achtergronden in seconden met Remove.bg.",
    "Suno AI laat je muziek genereren met alleen tekst.",
    "Runway ML maakt AI-video’s van tekst – perfect voor content creators!",
    "Quillbot helpt je teksten herschrijven en verbeteren met AI.",
    "Gamma.app maakt mooie AI-presentaties zonder PowerPoint.",
    "Leonardo AI genereert afbeeldingen in creatieve stijlen.",
    "ChatGPT helpt je e-mails, scripts en ideeën uitwerken.",
    "Kleurenpalet nodig? Gebruik huemint.com voor AI-gegenereerde kleuren.",
    "Durf je stem te klonen? Probeer ElevenLabs!",
]

tips_en = [
    "Use Copy.ai to generate blog posts and social media content automatically.",
    "Remove image backgrounds in seconds with Remove.bg.",
    "Suno AI lets you generate music from just text prompts.",
    "Runway ML creates AI videos from text – great for creators!",
    "Quillbot helps rewrite and improve your texts using AI.",
    "Gamma.app makes stylish presentations without PowerPoint.",
    "Leonardo AI creates unique images with different styles.",
    "ChatGPT helps draft emails, scripts, and ideas.",
    "Need a color palette? Try huemint.com’s AI-generated themes.",
    "Clone your voice? ElevenLabs can do that!",
]

def setup_db():
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    c.execute("CREATE TABLE IF NOT EXISTS users (chat_id INTEGER PRIMARY KEY, lang TEXT)")
    conn.commit()
    conn.close()

def add_user(chat_id, lang="nl"):
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    c.execute("INSERT OR IGNORE INTO users (chat_id, lang) VALUES (?, ?)", (chat_id, lang))
    conn.commit()
    conn.close()

def set_language(chat_id, lang):
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    c.execute("UPDATE users SET lang = ? WHERE chat_id = ?", (lang, chat_id))
    conn.commit()
    conn.close()

def get_all_users():
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    c.execute("SELECT chat_id, lang FROM users")
    users = c.fetchall()
    conn.close()
    return users

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    keyboard = [
        [KeyboardButton("Nederlands"), KeyboardButton("English")]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
    await context.bot.send_message(chat_id=chat_id, text="Welkom! / Welcome! Kies je taal / Choose your language:", reply_markup=reply_markup)

async def handle_language(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    lang_choice = update.message.text
    lang = "nl" if "Nederlands" in lang_choice else "en"
    add_user(chat_id, lang)
    await context.bot.send_message(chat_id=chat_id, text="Je ontvangt nu dagelijks een AI-tip! / You’ll now get a daily AI tip!")

async def send_daily_tip(app):
    index = datetime.now().timetuple().tm_yday % len(tips_nl)
    users = get_all_users()
    for chat_id, lang in users:
        tip = tips_nl[index] if lang == "nl" else tips_en[index]
        message = f"{tip}\n\n[Bekijk de tool]({LINK})" if lang == "nl" else f"{tip}\n\n[Try the tool]({LINK})"
        try:
            await app.bot.send_message(chat_id=chat_id, text=message, parse_mode="Markdown")
        except Exception as e:
            print(f"Error sending to {chat_id}: {e}")

async def main():
    setup_db()
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", start))

    from telegram.ext import MessageHandler, filters
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_language))

    scheduler = BackgroundScheduler()
    scheduler.add_job(lambda: asyncio.create_task(send_daily_tip(app)), 'cron', hour=DAILY_HOUR, minute=0)
    scheduler.start()

    print("Bot is running...")
    await app.run_polling()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
