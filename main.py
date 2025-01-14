import os
from dotenv import load_dotenv
import logging
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart, Command
from aiogram.types import Message
import requests
import re
import yt_dlp

# Загрузка переменных окружения из файла .env
load_dotenv()

API_TOKEN = os.getenv('TELEGRAM_API_TOKEN')
YOUTUBE_API_KEY = os.getenv('YOUTUBE_API_KEY')
WEATHER_API_KEY = os.getenv('OPENWEATHERMAP_API_KEY')

# Настройка логирования
logging.basicConfig(level=logging.INFO)

# Инициализация бота и диспетчера
bot = Bot(token=API_TOKEN)
dp = Dispatcher()


# Пример хендлера с использованием CommandStart
@dp.message(CommandStart())
async def start(message: Message):
    await message.answer("Привет! Отправьте мне ссылку на YouTube-видео, и я пришлю информацию о нем.")


# Пример хендлера с использованием Command
@dp.message(Command(commands=["help"]))
async def help_command(message: Message):
    await message.answer("Этот бот умеет выполнять команды:\n/start\n/help\n/weather")


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


# Прописываем хендлер для обработки ссылок на YouTube
@dp.message(lambda message: re.match(r'https?://(www\.)?youtube\.com/watch\?v=.+', message.text))
async def youtube_info(message: Message):
    url = message.text
    if not re.match(r"^https://www\.youtube\.com/watch\?v=[a-zA-Z0-9_-]+$", url):
        await message.reply("Некорректная ссылка на YouTube. Пожалуйста, отправьте корректную ссылку.")
        return

    try:
        ydl_opts = {}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(url, download=False)
            title = info_dict.get('title', None)
            author = info_dict.get('uploader', None)
            description = info_dict.get('description', None)
            await message.reply(f"**Название:** {title}\n**Автор:** {author}\n**Описание:** {description}")
    except Exception as e:
        logging.error(f"Произошла ошибка при обработке ссылки: {e}")
        await message.reply(f"Произошла ошибка при обработке ссылки. Ошибка: {str(e)}")


async def main():
    dp.message.register(start, CommandStart())
    dp.message.register(help_command, Command(commands=["help"]))
    dp.message.register(youtube_info,
                        lambda message: re.match(r'https?://(www\.)?youtube\.com/watch\?v=.+', message.text))

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
