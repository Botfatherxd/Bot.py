import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from datetime import datetime

TOKEN = "8667734362:AAGIWC0f3HdnEINFXdtqNIC-YuDlijJ5yDQ"

ADMIN_USERNAME = "userzubik"  # без @
CHANNEL = "@bomjreid"

bot = Bot(token=TOKEN)
dp = Dispatcher()

waiting_users = set()
pending_posts = {}  # id сообщения -> данные

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

# --- маска ---
def mask_username(username: str):
    if not username:
        return "unknown"
    if len(username) <= 4:
        return username[0] + "***"
    return username[:2] + "***" + username[-2:]


# --- START ---
@dp.message(CommandStart())
async def start(message: types.Message):
    await message.answer("Привет 👋\nВыбери действие:", reply_markup=keyboard)


# --- КНОПКИ ---
@dp.message(lambda m: m.text == "Союз")
async def union(message: types.Message):
    await message.answer(
        "🤝 Для вступления в союз свяжитесь с @userzubik\n"
        "Вам объяснят условия и дальнейшие действия."
    )

@dp.message(lambda m: m.text == "Информация")
async def info(message: types.Message):
    await message.answer(
        "ℹ️ Информация о системе\n\n"
        "Администрирование: @bomjreid"
    )

@dp.message(lambda m: m.text == "Слить")
async def sliv(message: types.Message):
    waiting_users.add(message.from_user.id)
    await message.answer(
        "⚠️ Подача заявки\n\n"
        "📸 фото ОБЯЗАТЕЛЬНО\n"
        "📝 описание + намерения\n\n"
        "Без фото — отказ."
    )


# --- ПРИЁМ ---
@dp.message()
async def handler(message: types.Message):
    if message.from_user.id not in waiting_users:
        return

    if not message.photo:
        await message.answer("❌ Нужно фото.")
        return

    waiting_users.remove(message.from_user.id)

    username_masked = mask_username(message.from_user.username or "unknown")

    text = (
        f"🔥 НОВАЯ ЗАЯВКА\n"
        f"👤 {username_masked}\n"
        f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        f"{message.caption or ''}"
    )

    file_id = message.photo[-1].file_id

    # отправка админу
    admin_msg = await bot.send_photo(
        chat_id=f"@{ADMIN_USERNAME}",
        photo=file_id,
        caption=text,
        reply_markup=types.InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    types.InlineKeyboardButton(text="✅ Принять", callback_data="approve"),
                    types.InlineKeyboardButton(text="❌ Отклонить", callback_data="reject"),
                ]
            ]
        )
    )

    # сохраняем заявку
    pending_posts[admin_msg.message_id] = {
        "photo": file_id,
        "text": text
    }

    await message.answer("✅ Заявка отправлена на проверку.")


# --- CALLBACK ---
@dp.callback_query(lambda c: c.data in ["approve", "reject"])
async def callbacks(callback: types.CallbackQuery):
    message_id = callback.message.message_id

    if message_id not in pending_posts:
        await callback.answer("Уже обработано")
        return

    data = pending_posts.pop(message_id)

    # только админ может нажимать
    if callback.from_user.username != ADMIN_USERNAME:
        await callback.answer("Нет доступа", show_alert=True)
        return

    if callback.data == "approve":
        # отправка в канал
        await bot.send_photo(
            chat_id=CHANNEL,
            photo=data["photo"],
            caption=data["text"]
        )
        await callback.message.edit_caption(
            callback.message.caption + "\n\n✅ ОДОБРЕНО"
        )

    else:
        await callback.message.edit_caption(
            callback.message.caption + "\n\n❌ ОТКЛОНЕНО"
        )

    await callback.answer("Готово")


# --- RUN ---
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
