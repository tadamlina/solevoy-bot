import asyncio
import os
import re
import csv
import random
from datetime import datetime
from aiogram import Bot, Dispatcher, types, F
from aiogram.types import Message
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from dotenv import load_dotenv

# Загружаем токен из .env
load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")

# Создаём бота и диспетчер
bot = Bot(token=TOKEN)
dp = Dispatcher(storage=MemoryStorage())

# Состояния
class Form(StatesGroup):
    waiting_for_your_birthday = State()
    waiting_for_partner_birthday = State()

# Стартовая команда
@dp.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    print(f"[{message.from_user.full_name}] стартовал бота")
    await message.answer("привет, я солевой бот ебал тебя в рот. сейчас я проверю вашу совместимость. др свое сюда пиши (дд.мм.гггг):")
    await state.set_state(Form.waiting_for_your_birthday)

# Получаем свою дату
@dp.message(Form.waiting_for_your_birthday)
async def your_birthday(message: Message, state: FSMContext):
    print(f"получена первая дата: {message.text}")
    if not re.match(r"\d{2}\.\d{2}\.\d{4}", message.text):
        await message.answer("Неправильно др пишешь, лейм. Введи в формате дд.мм.гггг:")
        return
    await state.update_data(your_date=message.text)
    await message.answer("др кента или кентушки сюда быстро:")
    await state.set_state(Form.waiting_for_partner_birthday)

# Получаем дату партнёра и считаем всё
@dp.message(Form.waiting_for_partner_birthday)
async def partner_birthday(message: Message, state: FSMContext):
    print(f"получена вторая дата: {message.text}")

    if message.text.strip() == "02.12.2003":
        await message.answer("сосал")
        await state.clear()
        print("пасхалка сработала")
        return

    if not re.match(r"\d{2}\.\d{2}\.\d{4}", message.text):
        await message.answer("Неправильно др пишешь, реально лейм, с первого раза не понял ало. Введи в формате дд.мм.гггг:")
        return

    data = await state.get_data()
    your_date = data.get("your_date")
    partner_date = message.text

    # Чистый рандом
    compatibility = random.randint(0, 100)

    # Комментарий по результату
    if compatibility > 90:
        comment = "ну вы реально сахарные пупсики няшечки совет да любовь"
    elif compatibility > 70:
        comment = "шоша со своим мужиком будут завидовать красоте вашей любви, но все-таки не прям обольщайтесь"
    elif compatibility > 50:
        comment = "вы как скайсы на зубах мс улыбочки, вроде красиво, но зубочисткой лучше не лезть"
    elif compatibility > 30:
        comment = "не ну как бы вы, конечно, можете попробовать, ну либо сразу 500 дней лета пересмотреть. в целом слушать деревянных китов и песню о привязанности и жестко чувствовать тоже вайбик"
    else:
        comment = "ну это реально жестко, ваши шансы примерно как у меня с робертом смитом"

    print(f"совместимость рассчитана: {compatibility}%")

    try:
        with open("logs.csv", "a", newline="", encoding="utf-8") as file:
            writer = csv.writer(file, delimiter=";")
            writer.writerow([
                message.from_user.id,
                message.from_user.full_name,
                message.from_user.username or "нет",
                your_date,
                partner_date,
                compatibility,
                datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            ])
        print("запись в CSV прошла успешно")
    except Exception as e:
        print("ошибка при записи в CSV:", e)

    await message.answer(f"Совместимость: {compatibility}%\n{comment}")
    await state.clear()
    print("ответ отправлен пользователю и состояние сброшено")

# Запуск
async def main():
    print("[бот активен] Солевой демон выехал по душам")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())