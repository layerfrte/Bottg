import os
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import CommandStart
from aiogram.enums import ChatMemberStatus

TOKEN = os.getenv("8783657392:AAFF6-DvFCDzMk8nnwwQeqO9xdD-VynR2rc")

CHANNEL_ID = -1003953850624  # поменяешь на свой
CHANNEL_LINK = "https://t.me/+emOVfai39ExlOWVi"

bot = Bot(token=TOKEN)
dp = Dispatcher()

# Кнопка канала
subscribe_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="📢 Перейти в канал", url=CHANNEL_LINK)],
        [InlineKeyboardButton(text="✅ Я подписался", callback_data="check")]
    ]
)

# Меню после проверки
menu_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="🔥 Меню", callback_data="menu")]
    ]
)

@dp.message(CommandStart())
async def start(message: types.Message):
    await message.answer(
        "Чтобы пользоваться ботом, подпишитесь на канал 👇",
        reply_markup=subscribe_kb
    )

@dp.callback_query(lambda c: c.data == "check")
async def check_sub(callback: types.CallbackQuery):
    user_id = callback.from_user.id

    try:
        member = await bot.get_chat_member(CHANNEL_ID, user_id)

        if member.status in [
            ChatMemberStatus.MEMBER,
            ChatMemberStatus.ADMINISTRATOR,
            ChatMemberStatus.CREATOR
        ]:
            await callback.message.edit_text(
                "✅ Доступ открыт!",
                reply_markup=menu_kb
            )
        else:
            await callback.answer("❌ Ты не подписан", show_alert=True)

    except:
        await callback.answer("❌ Сначала подпишись на канал", show_alert=True)

@dp.callback_query(lambda c: c.data == "menu")
async def menu(callback: types.CallbackQuery):
    await callback.message.answer("Меню открыто 🔥")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())