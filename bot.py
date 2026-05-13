import os
import asyncio
import sqlite3
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ChatJoinRequest

TOKEN = os.getenv("TOKEN")

CHANNEL_ID = -1003953850624
CHANNEL_LINK = "https://t.me/+ED2sSGi62BNjZTdi"

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

# ======================
# 💾 SQLITE БАЗА
# ======================
conn = sqlite3.connect("users.db")
cur = conn.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY
)
""")
conn.commit()

def add_user(user_id: int):
    cur.execute("INSERT OR IGNORE INTO users (user_id) VALUES (?)", (user_id,))
    conn.commit()

def user_exists(user_id: int):
    cur.execute("SELECT user_id FROM users WHERE user_id=?", (user_id,))
    return cur.fetchone() is not None

# ======================
# КНОПКИ
# ======================
join_kb = InlineKeyboardMarkup().add(
    InlineKeyboardButton("📢 Подать заявку", url=CHANNEL_LINK)
)

menu_kb = InlineKeyboardMarkup().add(
    InlineKeyboardButton("🔥 Меню", callback_data="menu")
)

# ======================
# /START
# ======================
@dp.message_handler(commands=["start"])
async def start(message: types.Message):
    user_id = message.from_user.id

    # если уже есть заявка → меню
    if user_exists(user_id):
        await message.answer(
            "✅ Доступ открыт!\n\n📋 МЕНЮ:\n- Профиль\n- Настройки\n- Инфо",
            reply_markup=menu_kb
        )
        return

    await message.answer(
        "❌ Сначала подай заявку в канал 👇",
        reply_markup=join_kb
    )

# ======================
# ЗАЯВКА В КАНАЛ
# ======================
@dp.chat_join_request_handler()
async def join_request(update: ChatJoinRequest):
    user_id = update.from_user.id

    add_user(user_id)

    print(f"📥 Новая заявка: {user_id}")

    # можно уведомление в канал
    try:
        await bot.send_message(
            CHANNEL_ID,
            f"📥 +1 заявка\n👤 ID: {user_id}\n🎯 Цель 1000 заявок!"
        )
    except:
        print("❌ не смог отправить сообщение в канал")

# ======================
# МЕНЮ
# ======================
@dp.callback_query_handler(lambda c: c.data == "menu")
async def menu(callback: types.CallbackQuery):
    await callback.message.answer("🔥 Это меню бота")

# ======================
# RUN
# ======================
async def main():
    print("Bot started...")
    await dp.start_polling()

if __name__ == "__main__":
    asyncio.run(main())
