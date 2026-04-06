import asyncio
import logging
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart, Command
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

# --- НАСТРОЙКИ ---
API_TOKEN = '8738558325:AAEKECSj1E6cdZvV-JxYd1bwzb5NLzT3Q1o'
ADMIN_ID = 8290002488
FILE_NAME = 'users.txt'
# ВСТАВЬ ССЫЛКУ НА СВОЙ ТГ КАНАЛ ИЛИ ГРУППУ НИЖЕ:
GROUP_LINK = 'https://t.me/+-AK9x-ZN-6YzYmYx'

logging.basicConfig(level=logging.INFO)
bot = Bot(token=API_TOKEN)
dp = Dispatcher()


class RegState(StatesGroup):
    waiting_for_mc_nick = State()


def save_to_db(user_id, name, username, mc_nick):
    try:
        with open(FILE_NAME, 'r', encoding='utf-8') as f:
            lines = [l for l in f.readlines() if l.strip()]
            count = len(lines) + 1
    except FileNotFoundError:
        count = 1

    line = f"{count}. ID: {user_id} | Name: {name} | User: {username} | MC: {mc_nick}\n"
    with open(FILE_NAME, 'a', encoding='utf-8') as f:
        f.write(line)


@dp.message(CommandStart())
async def cmd_start(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    try:
        with open(FILE_NAME, 'r', encoding='utf-8') as f:
            if str(user_id) in f.read():
                await message.answer("Вы уже зарегистрированы!")
                return
    except FileNotFoundError:
        pass

    await message.answer("🎮 Привет! Введи свой ник в Minecraft для регистрации:")
    await state.set_state(RegState.waiting_for_mc_nick)


@dp.message(RegState.waiting_for_mc_nick)
async def get_mc_nick(message: types.Message, state: FSMContext):
    mc_nick = message.text.strip()
    user_id = message.from_user.id
    name = message.from_user.first_name
    username = f"@{message.from_user.username}" if message.from_user.username else "NoUser"

    await state.clear()
    await message.answer("⌛️ Твоя заявка отправлена админу. Ожидай одобрения!")

    builder = InlineKeyboardBuilder()
    builder.row(
        types.InlineKeyboardButton(text="✅ Принять", callback_data=f"ok_{user_id}"),
        types.InlineKeyboardButton(text="❌ Отклонить", callback_data=f"no_{user_id}")
    )

    await bot.send_message(
        ADMIN_ID,
        f"🔔 Новая заявка!\n\n"
        f"👤 Имя: {name}\n"
        f"🔗 Юзер: {username}\n"
        f"🎮 Minecraft: {mc_nick}\n"
        f"🆔 ID: {user_id}",
        reply_markup=builder.as_markup()
    )


@dp.callback_query(F.data.startswith("ok_"))
async def accept_user(callback: types.CallbackQuery):
    user_id = callback.data.split("_")[1]
    text = callback.message.text

    try:
        name = text.split("Имя: ")[1].split("\n")[0]
        username = text.split("Юзер: ")[1].split("\n")[0]
        mc_nick = text.split("Minecraft: ")[1].split("\n")[0]
    except:
        name, username, mc_nick = "Unknown", "Unknown", "Unknown"

    save_to_db(user_id, name, username, mc_nick)

    await callback.message.edit_text(f"✅ Игрок {mc_nick} добавлен в список.")

    # СООБЩЕНИЕ С ССЫЛКОЙ
    try:
        await bot.send_message(
            user_id,
            f"🎉 Поздравляем, {mc_nick}! Твоя заявка одобрена.\n\n"
            f"Вот ссылка на наш Телеграм: {GROUP_LINK}"
        )
    except:
        pass


@dp.callback_query(F.data.startswith("no_"))
async def decline_user(callback: types.CallbackQuery):
    user_id = callback.data.split("_")[1]
    await callback.message.edit_text(f"❌ Заявка {user_id} отклонена.")
    try:
        await bot.send_message(user_id, "К сожалению, доступ отклонен.")
    except:
        pass


async def main():
    print("Бот запущен и ждет заявок...")
    await dp.start_polling(bot)


# Исправлено: добавлены подчеркивания __
if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        print("Бот выключен")