import os
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ChatJoinRequest

TOKEN = os.getenv("TOKEN")

CHANNEL_ID = -1003953850624
CHANNEL_LINK = "https://t.me/+ED2sSGi62BNjZTdi"

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

# счётчик заявок
request_count = 0

# старт
start_kb = InlineKeyboardMarkup().add(
    InlineKeyboardButton("📢 Подписаться на канал", url=CHANNEL_LINK)
).add(
    InlineKeyboardButton("➡️ Проверить", callback_data="next")
)

menu_kb = InlineKeyboardMarkup().add(
    InlineKeyboardButton("🔥 Меню", callback_data="menu")
)

# /start
@dp.message_handler(commands=["start"])
async def start(message: types.Message):
    await message.answer(
        "ты не подал заявку на канал(👇",
        reply_markup=start_kb
    )

# Кнопка продолжить
@dp.callback_query_handler(lambda c: c.data == "next")
async def next_step(callback: types.CallbackQuery):
    await callback.message.edit_text(
        "📋 МЕНЮ\n\n"
        "• Профиль\n"
        "• Настройки\n"
        "• Инфо\n\n"
        "Выбери действие:",
        reply_markup=menu_kb
    )

# лог заявок
@dp.chat_join_request_handler()
async def join_request(update: ChatJoinRequest):
    global request_count

    request_count += 1
    user = update.from_user

    text = (
        f"📥 +1 заявка\n"
        f"👤 {user.full_name}\n"
        f"ID: {user.id}\n\n"
        f"📊 Сейчас заявок: {request_count}\n"
        f"🎯 Цель 1000 заявок!"
    )

    print(text)

    # отправка в канал
    try:
        await bot.send_message(CHANNEL_ID, text)
    except:
        print("не удалось отправить в канал")

# меню кнопка
@dp.callback_query_handler(lambda c: c.data == "menu")
async def menu(callback: types.CallbackQuery):
    await callback.message.answer("Это меню бота 🔥")

async def main():
    print("Bot started...")
    await dp.start_polling()

if __name__ == "__main__":
    asyncio.run(main())
