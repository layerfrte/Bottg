import os
import asyncio
import sqlite3

from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ChatJoinRequest

TOKEN = os.getenv("TOKEN")

CHANNEL_ID = -1003953850624
CHANNEL_LINK = "https://t.me/+emOVfai39ExlOWVi"

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

# =========================
# DATABASE
# =========================
conn = sqlite3.connect("bot.db")
cur = conn.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    invited_by INTEGER
)
""")

cur.execute("""
CREATE TABLE IF NOT EXISTS refs (
    user_id INTEGER,
    app TEXT
)
""")

cur.execute("""
CREATE TABLE IF NOT EXISTS requests (
    user_id INTEGER PRIMARY KEY
)
""")

conn.commit()

# =========================
# HELPERS
# =========================
def add_user(user_id):
    cur.execute("INSERT OR IGNORE INTO users VALUES (?, ?)", (user_id, None))
    conn.commit()

def is_new_user(user_id):
    cur.execute("SELECT user_id FROM users WHERE user_id=?", (user_id,))
    return cur.fetchone() is None

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
    InlineKeyboardButton("📢 Подписаться", url=CHANNEL_LINK)
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
# START
# =========================
@dp.message_handler(commands=["start"])
async def start(message: types.Message):
    user_id = message.from_user.id
    args = message.get_args()

    referrer_id = None
    app = None

    # =========================
    # РЕФ ССЫЛКА
    # =========================
    if args and "_" in args:
        try:
            app, referrer_id = args.split("_")
            referrer_id = int(referrer_id)
        except:
            referrer_id = None

    # =========================
    # ПРОВЕРКА ЗАЯВКИ
    # =========================
    cur.execute("SELECT * FROM requests WHERE user_id=?", (user_id,))
    req = cur.fetchone()

    if not req:
        await message.answer(
            "❌ Сначала подай заявку в канал 👇",
            reply_markup=join_kb
        )
        return

    # =========================
    # НОВЫЙ ПОЛЬЗОВАТЕЛЬ?
    # =========================
    cur.execute("SELECT * FROM users WHERE user_id=?", (user_id,))
    existing_user = cur.fetchone()

    if not existing_user:

        # сохраняем нового пользователя
        cur.execute(
            "INSERT INTO users (user_id, invited_by) VALUES (?, ?)",
            (user_id, referrer_id)
        )
        conn.commit()

        # =========================
        # ЗАСЧИТАТЬ РЕФЕРАЛ
        # =========================
        if (
            referrer_id
            and referrer_id != user_id
            and app
        ):

            # не дублировать
            cur.execute(
                "SELECT * FROM refs WHERE user_id=? AND app=?",
                (referrer_id, app)
            )

            already = cur.fetchone()

            if not already:
                cur.execute(
                    "INSERT INTO refs VALUES (?, ?)",
                    (referrer_id, app)
                )
                conn.commit()

                # уведомление
                try:
                    await bot.send_message(
                        referrer_id,
                        f"📈 +1 реферал для {app}!"
                    )
                except:
                    pass

    # =========================
    # МЕНЮ
    # =========================
    await message.answer(
        "Привет. Выбирай на какую приватку хочешь софт!",
        reply_markup=menu_kb
    )

# =========================
# JOIN REQUEST
# =========================
@dp.chat_join_request_handler()
async def join_request(update: ChatJoinRequest):
    user_id = update.from_user.id

    cur.execute("INSERT OR IGNORE INTO requests VALUES (?)", (user_id,))
    conn.commit()

    add_user(user_id)

    try:
        await bot.send_message(
            CHANNEL_ID,
            f"📥 +1 заявка\n👤 ID: {user_id}\n🌏Дальше - меньше!"
        )
    except:
        pass

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
# APPS + REFS
# =========================
@dp.callback_query_handler(lambda c: c.data.startswith("app_"))
async def apps(callback: types.CallbackQuery):
    app = callback.data.replace("app_", "")
    user_id = callback.from_user.id

    refs = count_refs(user_id, app)

    if refs >= 10:
        await callback.message.edit_text(
            "✅ Вы успешно выполнили условия!\nОжидайте в течении 1 часа..",
            reply_markup=back_kb
        )
    else:
        await callback.message.edit_text(
            f"❌ Для {app} нужно 10 рефералов\n\n"
            f"👥 Сейчас: {refs}/10\n\n"
            f"🔥 Ваша ссылка:\n{ref_link(user_id, app)}",
            reply_markup=back_kb
        )

# =========================
# ADMIN
# =========================

ADMIN_USERNAME = "vkffe"

admin_kb = InlineKeyboardMarkup(row_width=1).add(
    InlineKeyboardButton("👥 Пользователи", callback_data="admin_users")
)

# =========================
# /admin
# =========================
@dp.message_handler(commands=["admin"])
async def admin(message: types.Message):

    if message.from_user.username != ADMIN_USERNAME:
        return

    await message.answer(
        "⚙️ Админ панель",
        reply_markup=admin_kb
    )

# =========================
# СПИСОК ПОЛЬЗОВАТЕЛЕЙ
# =========================
@dp.callback_query_handler(lambda c: c.data == "admin_users")
async def admin_users(callback: types.CallbackQuery):

    if callback.from_user.username != ADMIN_USERNAME:
        return

    cur.execute("SELECT user_id FROM users")
    users = cur.fetchall()

    kb = InlineKeyboardMarkup(row_width=1)

    for user in users[:50]:

        user_id = user[0]

        kb.add(
            InlineKeyboardButton(
                f"👤 {user_id}",
                callback_data=f"user_{user_id}"
            )
        )

    await callback.message.edit_text(
        "👥 Пользователи:",
        reply_markup=kb
    )

# =========================
# ИНФА О ПОЛЬЗОВАТЕЛЕ
# =========================
@dp.callback_query_handler(lambda c: c.data.startswith("user_"))
async def user_info(callback: types.CallbackQuery):

    if callback.from_user.username != ADMIN_USERNAME:
        return

    user_id = int(callback.data.split("_")[1])

    # сколько рефов
    cur.execute(
        "SELECT COUNT(*) FROM refs WHERE user_id=?",
        (user_id,)
    )

    refs = cur.fetchone()[0]

    # кто пригласил
    cur.execute(
        "SELECT invited_by FROM users WHERE user_id=?",
        (user_id,)
    )

    invited = cur.fetchone()

    invited_by = invited[0] if invited else None

    text = (
        f"👤 USER: {user_id}\n\n"
        f"📈 Рефералов: {refs}\n"
        f"🔗 Пришел по рефке: {invited_by}"
    )

    await callback.message.edit_text(text)

# =========================
# ВЫДАТЬ РЕФЕРАЛ
# =========================
@dp.message_handler(commands=["giveref"])
async def give_ref(message: types.Message):

    if message.from_user.username != ADMIN_USERNAME:
        return

    args = message.text.split()

    # /giveref ID APP
    if len(args) < 3:
        await message.answer(
            "Пример:\n/giveref 123456789 StandKnife"
        )
        return

    target_id = int(args[1])
    app = args[2]

    # добавляем реф
    cur.execute(
        "INSERT INTO refs VALUES (?, ?)",
        (target_id, app)
    )
    conn.commit()

    # сколько стало
    cur.execute(
        "SELECT COUNT(*) FROM refs WHERE user_id=? AND app=?",
        (target_id, app)
    )

    total = cur.fetchone()[0]

    # уведомление
    try:
        await bot.send_message(
            target_id,
            f"📈 По вашей ссылке перешел +1 реферал\n\n"
            f"👥 Сейчас рефералов для {app}: {total}/5"
        )
    except:
        pass

    await message.answer(
        f"✅ Пользователю {target_id} добавлен +1 реферал"
    )

# =========================
# RUN
# =========================
async def main():
    print("Bot started")
    await dp.start_polling()

if __name__ == "__main__":
    asyncio.run(main())
