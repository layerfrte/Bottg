import os
import asyncio
import sqlite3
import random
import string

from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ChatJoinRequest

TOKEN = os.getenv("TOKEN")

CHANNEL_ID = -1003953850624
CHANNEL_LINK = "https://t.me/+emOVfai39ExlOWVi"

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

# =========================
# 💾 SQLITE
# =========================
conn = sqlite3.connect("bot.db")
cur = conn.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    ref_code TEXT,
    invited_by TEXT
)
""")

cur.execute("""
CREATE TABLE IF NOT EXISTS referrals (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    referrer TEXT,
    user_id INTEGER
)
""")

conn.commit()

# =========================
# HELPERS
# =========================
def generate_code():
    return ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(6))

def get_user(user_id):
    cur.execute("SELECT user_id, ref_code, invited_by FROM users WHERE user_id=?", (user_id,))
    return cur.fetchone()

def create_user(user_id, ref_code=None, invited_by=None):
    cur.execute("INSERT OR IGNORE INTO users (user_id, ref_code, invited_by) VALUES (?, ?, ?)",
                (user_id, ref_code, invited_by))
    conn.commit()

def add_ref(referrer, user_id):
    cur.execute("SELECT * FROM referrals WHERE user_id=?", (user_id,))
    if cur.fetchone():
        return

    cur.execute("INSERT INTO referrals (referrer, user_id) VALUES (?, ?)", (referrer, user_id))
    conn.commit()

def count_refs(ref_code):
    cur.execute("SELECT COUNT(*) FROM referrals WHERE referrer=?", (ref_code,))
    return cur.fetchone()[0]

# =========================
# MENU
# =========================
def menu_kb():
    return InlineKeyboardMarkup(row_width=1).add(
        InlineKeyboardButton("1. StandKnife", callback_data="app_StandKnife"),
        InlineKeyboardButton("2. StandChillow", callback_data="app_StandChillow"),
        InlineKeyboardButton("3. StandLeo", callback_data="app_StandLeo"),
        InlineKeyboardButton("4. Project Evolution", callback_data="app_Project"),
        InlineKeyboardButton("5. Standoff 2", callback_data="app_Standoff")
    )

# =========================
# /START
# =========================
@dp.message_handler(commands=["start"])
async def start(message: types.Message):
    user_id = message.from_user.id
    args = message.get_args()

    user = get_user(user_id)

    # создаём код если нет
    if not user:
        code = generate_code()
        create_user(user_id, ref_code=code, invited_by=args if args else None)
    else:
        code = user[1]

    # если есть реферал
    if args:
        create_user(user_id, ref_code=code, invited_by=args)
        add_ref(args, user_id)

    # проверка доступа
    refs = count_refs(code)

    if refs >= 5:
        await message.answer(
            "✅ Вы успешно выполнили условия!\nОжидайте в течении 1 часа..",
            reply_markup=types.InlineKeyboardMarkup().add(
                types.InlineKeyboardButton("🔥 Меню", callback_data="menu")
            )
        )
    else:
        await message.answer(
            f"❌ Чтобы получить доступ — пригласи 5 рефералов\n"
            f"👥 Сейчас: {refs}/5\n\n"
            f"Вот твоя ссылка:\n"
            f"https://t.me/ForclocBot?start={code}"
        )

# =========================
# JOIN REQUEST
# =========================
@dp.chat_join_request_handler()
async def join_request(update: ChatJoinRequest):
    user_id = update.from_user.id
    create_user(user_id)

# =========================
# MENU
# =========================
@dp.callback_query_handler(lambda c: c.data == "menu")
async def menu(callback: types.CallbackQuery):
    await callback.message.edit_text(
        "Привет. Выбирай на какую приватку хочешь софт!",
        reply_markup=menu_kb()
    )

# =========================
# APPS
# =========================
@dp.callback_query_handler(lambda c: c.data.startswith("app_"))
async def apps(callback: types.CallbackQuery):
    name = callback.data.replace("app_", "")

    await callback.message.edit_text(
        f"❌ Чтобы скачать софт на {name} тебе надо пригласить 5 рефералов!\n\n"
        "Извините за то что нужны рефералы, софт бесплатный, но из-за нагрузки это обязательно.\n\n"
        "🔥 Вот твоя ссылка выше 👆"
    )

# =========================
async def main():
    print("Bot started")
    await dp.start_polling()

if __name__ == "__main__":
    asyncio.run(main())
