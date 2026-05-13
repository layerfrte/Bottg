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

# =========================
# 💾 DATABASE
# =========================
conn = sqlite3.connect("bot.db")
cur = conn.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY
)
""")

cur.execute("""
CREATE TABLE IF NOT EXISTS refs (
    user_id INTEGER,
    app TEXT
)
""")

conn.commit()

# =========================
# HELPERS
# =========================
def add_user(user_id):
    cur.execute("INSERT OR IGNORE INTO users VALUES (?)", (user_id,))
    conn.commit()

def is_user(user_id):
    cur.execute("SELECT user_id FROM users WHERE user_id=?", (user_id,))
    return cur.fetchone() is not None

def add_ref(user_id, app):
    cur.execute("SELECT * FROM refs WHERE user_id=? AND app=?", (user_id, app))
    if cur.fetchone():
        return False
    cur.execute("INSERT INTO refs VALUES (?, ?)", (user_id, app))
    conn.commit()
    return True

def count_refs(user_id, app):
    cur.execute("SELECT COUNT(*) FROM refs WHERE user_id=? AND app=?", (user_id, app))
    return cur.fetchone()[0]

def ref_link(user_id, app):
    return f"https://t.me/ForclocBot?start={app}_{user_id}"

# =========================
# KEYBOARDS
# =========================
join_kb = InlineKeyboardMarkup().add(
    InlineKeyboardButton("📢 Подать заявку", url=CHANNEL_LINK)
)

menu_kb = InlineKeyboardMarkup(row_width=1).add(
    InlineKeyboardButton("1. StandKnife", callback_data="app_StandKnife"),
    InlineKeyboardButton("2. StandChillow", callback_data="app_StandChillow"),
    InlineKeyboardButton("3. StandLeo", callback_data="app_StandLeo"),
    InlineKeyboardButton("4. Project Evolution", callback_data="app_Project"),
    InlineKeyboardButton("5. Standoff 2", callback_data="app_Standoff")
)

back_kb = InlineKeyboardMarkup().add(
    InlineKeyboardButton("🔙 Назад в меню", callback_data="menu")
)

# =========================
# START (ГЛАВНАЯ ЛОГИКА)
# =========================
@dp.message_handler(commands=["start"])
async def start(message: types.Message):
    user_id = message.from_user.id
    args = message.get_args()

    # 🔥 реферал засчитываем
    if args and "_" in args:
        app, referrer_id = args.split("_")
        try:
            add_ref(int(referrer_id), app)
        except:
            pass

    # 🔥 проверка реального доступа в канал
    try:
        member = await bot.get_chat_member(CHANNEL_ID, user_id)

        if member.status not in ["member", "administrator", "creator"]:
            await message.answer(
                "❌ Сначала подай заявку в канал 👇",
                reply_markup=join_kb
            )
            return
    except:
        await message.answer("❌ Ошибка проверки канала")
        return

    # если всё ок → добавляем в базу
    add_user(user_id)

    await message.answer(
        "Привет. Выбирай на какую приватку хочешь софт!",
        reply_markup=menu_kb
    )

# =========================
# JOIN REQUEST (фикс заявки)
# =========================
@dp.chat_join_request_handler()
async def join_request(update: ChatJoinRequest):
    user_id = update.from_user.id
    add_user(user_id)

# =========================
# MENU
# =========================
@dp.callback_query_handler(lambda c: c.data == "menu")
async def menu(callback: types.CallbackQuery):
    await callback.message.edit_text(
        "Привет. Выбирай на какую приватку хочешь софт!",
        reply_markup=menu_kb
    )

# =========================
# APPS + REF SYSTEM
# =========================
@dp.callback_query_handler(lambda c: c.data.startswith("app_"))
async def apps(callback: types.CallbackQuery):
    app = callback.data.replace("app_", "")
    user_id = callback.from_user.id

    refs = count_refs(user_id, app)

    if refs >= 5:
        await callback.message.edit_text(
            "✅ Вы успешно выполнили условия!\nОжидайте в течении 1 часа..",
            reply_markup=back_kb
        )
    else:
        await callback.message.edit_text(
            f"❌ Для {app} нужно 5 рефералов\n\n"
            f"👥 Сейчас: {refs}/5\n\n"
            f"🔥 Твоя ссылка:\n{ref_link(user_id, app)}",
            reply_markup=back_kb
        )

# =========================
# RUN
# =========================
async def main():
    print("Bot started")
    await dp.start_polling()

if __name__ == "__main__":
    asyncio.run(main())
