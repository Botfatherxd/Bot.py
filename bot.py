import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from datetime import datetime

TOKEN = "8667734362:AAGIWC0f3HdnEINFXdtqNIC-YuDlijJ5yDQ"

ADMIN_USERNAME = "userzubik"  # без @
ADMIN_ID = None

bot = Bot(token=TOKEN)
dp = Dispatcher()

waiting_users = set()

keyboard = types.ReplyKeyboardMarkup(
    keyboard=[
        [
            types.KeyboardButton(text="Союз"),
            types.KeyboardButton(text="Слить"),
        ],
        [
            types.KeyboardButton(text="Информация"),
        ]
    ],
    resize_keyboard=True
)


# -------- START --------
@dp.message(CommandStart())
async def start(message: types.Message):
    global ADMIN_ID

    # фиксируем админа по username
    if message.from_user.username == ADMIN_USERNAME:
        ADMIN_ID = message.from_user.id

    await message.answer(
        "Привет! 👋\nВыбери действие:",
        reply_markup=keyboard
    )


# -------- BUTTONS --------
@dp.message(lambda msg: msg.text == "Союз")
async def union(message: types.Message):
    await message.answer("Вам к @userzubik")


@dp.message(lambda msg: msg.text == "Информация")
async def info(message: types.Message):
    await message.answer("Юзернейм: @bomjreid")


@dp.message(lambda msg: msg.text == "Слить")
async def sliv(message: types.Message):
    waiting_users.add(message.from_user.id)

    await message.answer(
        "⚠️ Отправьте сообщение или фото с:\n"
        "— доказательством\n"
        "— описанием ситуации\n"
        "— своими намерениями"
    )


# -------- HANDLE SLIV --------
@dp.message()
async def handle_sliv(message: types.Message):
    global ADMIN_ID

    if message.from_user.id not in waiting_users:
        return

    waiting_users.remove(message.from_user.id)

    username = message.from_user.username or "no_username"

    text_info = (
        f"🔥 НОВАЯ ЗАЯВКА НА СЛИВ\n"
        f"👤 От: @{username}\n"
        f"🆔 ID: {message.from_user.id}\n"
        f"⏰ Время: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
    )

    # если фото
    if message.photo:
        file_id = message.photo[-1].file_id
        caption = message.caption or ""

        if ADMIN_ID:
            await bot.send_photo(
                ADMIN_ID,
                photo=file_id,
                caption=text_info + caption
            )

    # если текст
    elif message.text:
        if ADMIN_ID:
            await bot.send_message(
                ADMIN_ID,
                text=text_info + message.text
            )

    await message.answer("✅ Заявка отправлена админу.")


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
