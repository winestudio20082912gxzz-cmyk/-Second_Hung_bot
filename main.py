from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    MessageHandler,
    CommandHandler,
    ContextTypes,
    filters,
)

from openai import OpenAI
from apscheduler.schedulers.asyncio import AsyncIOScheduler

import os
import random

BOT_TOKEN = os.getenv("BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
GROUP_ID = os.getenv("GROUP_ID")

client = OpenAI(api_key=OPENAI_API_KEY)

scheduler = AsyncIOScheduler()

used_posts = []

# AI Personality
SYSTEM_PROMPT = """
You are a calm literary Telegram channel editor.

Rules:
- Write naturally like a real human.
- Avoid too many emojis.
- Write clean Burmese text.
- Make readers emotionally interested.
- Use spacing beautifully.
- Sometimes use bold emotional hooks.
- Tone should feel like a modern Myanmar literary editor.
- Never sound robotic.
- Short posts are preferred.
"""

# START
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    await update.message.reply_text(
        "Second Hung AI is online."
    )

# WELCOME
async def welcome(update: Update, context: ContextTypes.DEFAULT_TYPE):

    for member in update.message.new_chat_members:

        await update.message.reply_text(
            f"{member.first_name} joined the conversation."
        )

# AI CHAT
async def ai_chat(update: Update, context: ContextTypes.DEFAULT_TYPE):

    text = update.message.text

    spam_words = ["http", "t.me", "spam"]

    for word in spam_words:
        if word in text.lower():
            await update.message.delete()
            return

    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {
                "role": "system",
                "content": SYSTEM_PROMPT
            },
            {
                "role": "user",
                "content": text
            }
        ]
    )

    reply = response.choices[0].message.content

    await update.message.reply_text(reply)

# GENERATE POST
async def generate_post(topic):

    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {
                "role": "system",
                "content": SYSTEM_PROMPT
            },
            {
                "role": "user",
                "content": (
                    f"Write a short Myanmar literary Telegram post about {topic}. "
                    "Make it emotional, clean, readable, and unique."
                )
            }
        ]
    )

    return response.choices[0].message.content

# MORNING POST
async def morning_post(bot):

    topics = [
        "hope",
        "morning thoughts",
        "moving on",
        "quiet love",
        "missing someone"
    ]

    text = await generate_post(random.choice(topics))

    await bot.send_message(
        chat_id=GROUP_ID,
        text=text
    )

# NOON POST
async def noon_post(bot):

    topics = [
        "relationships",
        "friendship",
        "distance",
        "memories",
        "books"
    ]

    text = await generate_post(random.choice(topics))

    await bot.send_message(
        chat_id=GROUP_ID,
        text=text
    )

# NIGHT POST
async def night_post(bot):

    topics = [
        "night feelings",
        "loneliness",
        "old memories",
        "late night thoughts",
        "poetry"
    ]

    text = await generate_post(random.choice(topics))

    await bot.send_message(
        chat_id=GROUP_ID,
        text=text
    )

# MAIN
app = ApplicationBuilder().token(BOT_TOKEN).build()

app.add_handler(CommandHandler("start", start))

app.add_handler(
    MessageHandler(
        filters.StatusUpdate.NEW_CHAT_MEMBERS,
        welcome
    )
)

app.add_handler(
    MessageHandler(
        filters.TEXT & ~filters.COMMAND,
        ai_chat
    )
)

# SCHEDULE POSTS
scheduler.add_job(
    lambda: morning_post(app.bot),
    'cron',
    hour=7,
    minute=0
)

scheduler.add_job(
    lambda: noon_post(app.bot),
    'cron',
    hour=12,
    minute=0
)

scheduler.add_job(
    lambda: night_post(app.bot),
    'cron',
    hour=21,
    minute=0
)

scheduler.start()

print("Second Hung AI Running...")
app.run_polling()
