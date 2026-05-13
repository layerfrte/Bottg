import os
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ChatJoinRequest

TOKEN = os.getenv("TOKEN")

CHANNEL_ID = -1003953850624
CHANNEL_LINK = "https://t.me/+emOVfai39ExlOWVi"

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

# Кнопка
start_kb = InlineKeyboardMarkup().add(
    InlineKeyboardButton("📢 Перейти в канал", url=CHANNEL_LINK)
).add(
    InlineKeyboardButton("📌 Я подал заявку", callback_data="check")
)

@dp.message_handler(commands=["start"])
async def start(message: types.Message):
    await message.answer(
        "Чтобы получить доступ — подай заявку в канал 👇",
        reply_markup=start_kb
    )

# ЛОГ ЗАЯВОК (главная часть)
@dp.chat_join_request_handler()
async def join_request(update: ChatJoinRequest):
    user = update.from_user

    print("━━━━━━━━━━━━━━━━━━━━━━")
    print("📥 НОВАЯ ЗАЯВКА")
    print(f"ID: {user.id}")
    print(f"USERNAME: @{user.username}")
    print(f"NAME: {user.full_name}")
    print("━━━━━━━━━━━━━━━━━━━━━━")

@dp.callback_query_handler(lambda c: c.data == "check")
async def check(callback: types.CallbackQuery):
    await callback.answer("Заявка отслеживается, ожидай 👍", show_alert=True)

async def main():
    print("Bot started...")
    await dp.start_polling()

if __name__ == "__main__":
    asyncio.run(main())
