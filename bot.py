import os
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

TOKEN = os.getenv("TOKEN")

CHANNEL_ID = -1003953850624
CHANNEL_LINK = "https://t.me/+emOVfai39ExlOWVi"

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

subscribe_kb = InlineKeyboardMarkup().add(
    InlineKeyboardButton("📢 Канал", url=CHANNEL_LINK)
).add(
    InlineKeyboardButton("✅ Проверить", callback_data="check")
)

menu_kb = InlineKeyboardMarkup().add(
    InlineKeyboardButton("🔥 Меню", callback_data="menu")
)

@dp.message_handler(commands=["start"])
async def start(message: types.Message):
    await message.answer(
        "Подпишись на канал 👇",
        reply_markup=subscribe_kb
    )

@dp.callback_query_handler(lambda c: c.data == "check")
async def check(callback: types.CallbackQuery):
    user_id = callback.from_user.id

    try:
        member = await bot.get_chat_member(CHANNEL_ID, user_id)

        if member.status in ["member", "administrator", "creator"]:
            await callback.message.edit_text("✅ Доступ открыт", reply_markup=menu_kb)
        else:
            await callback.answer("❌ Ты не подписан", show_alert=True)

    except:
        await callback.answer("❌ Сначала подпишись", show_alert=True)

@dp.callback_query_handler(lambda c: c.data == "menu")
async def menu(callback: types.CallbackQuery):
    await callback.message.answer("Меню открыто 🔥")

async def main():
    await dp.start_polling()

if __name__ == "__main__":
    asyncio.run(main())
