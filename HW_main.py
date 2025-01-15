import os
from dotenv import load_dotenv
import logging
from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message
import requests
import random

# Загрузка переменных окружения из файла .env
load_dotenv()

API_TOKEN = os.getenv('TELEGRAM_API_TOKEN')
WEATHER_API_KEY = os.getenv('OPENWEATHERMAP_API_KEY')

# Настройка логирования
logging.basicConfig(level=logging.INFO)

# Инициализация бота и диспетчера
bot = Bot(token=API_TOKEN)
dp = Dispatcher()


# Пример хендлера с использованием CommandStart
@dp.message(CommandStart())
async def start(message: Message):
    await message.answer("Привет, я бот, который расскажет про погоду в вашем городе!")


# Пример хендлера с использованием Command
@dp.message(Command(commands=["help"]))
async def help_command(message: Message):
    await message.answer("Этот бот умеет выполнять команды:\n/start\n/help\n/weather\n/photo")

@dp.message(Command(commands=["photo"]))
async def photo(message: Message):
    list = ['https://img.freepik.com/free-photo/aerial-view-cityscape_181624-49144.jpg']
    rand_photo = random.choice(list)
    await message.answer_photo(photo=rand_photo, caption='Вот мой родной район Минска')


# Прописываем хендлер для команды /weather
@dp.message(Command(commands=["weather"]))
async def weather_command(message: Message):
    city = "minsk"
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={WEATHER_API_KEY}&units=metric&lang=ru"
    response = requests.get(url)
    data = response.json()

    if data["cod"] == 200:
        temperature = data["main"]["temp"]
        description = data["weather"][0]["description"]
        await message.answer(f"Погода в {city.capitalize()}:\nТемпература: {temperature}°C\nОписание: {description}")
    else:
        await message.answer("Не удалось получить прогноз погоды. Пожалуйста, попробуйте позже.")

@dp.message()
async def start(message: Message):
    await message.answer("Сформулируй вопрос по другому")
async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
