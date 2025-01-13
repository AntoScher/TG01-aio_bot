import os
from dotenv import load_dotenv
import logging
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.utils import executor
from pytube import YouTube
import re

# Загрузка переменных окружения из файла .env
load_dotenv()

API_TOKEN = os.getenv('TELEGRAM_API_TOKEN')
YOUTUBE_API_KEY = os.getenv('YOUTUBE_API_KEY')

# Настройка логирования
logging.basicConfig(level=logging.INFO)

# Инициализация бота и диспетчера
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)
dp.middleware.setup(LoggingMiddleware())

@dp.message_handler(commands=['start', 'help'])
async def send_welcome(message: types.Message):
    await message.reply("Привет! Отправьте мне ссылку на YouTube-видео, и я пришлю информацию о нем.")

@dp.message_handler(regexp=r'https?://(www\.)?youtube\.com/watch\?v=.+')
async def youtube_info(message: types.Message):
    url = message.text
    # проверка ссылки на корректность
    if not re.match(r"^https://www\.youtube\.com/watch\?v=[a-zA-Z0-9_-]+$", url):
        await message.reply("Некорректная ссылка на YouTube. Пожалуйста, отправьте корректную ссылку.")
        return

    try:
        yt = YouTube(url)
        title = yt.title
        author = yt.author
        description = yt.description
        await message.reply(f"**Название:** {title}\n**Автор:** {author}\n**Описание:** {description}")
    except Exception as e:
        logging.error(f"Произошла ошибка при обработке ссылки: {e}")
        await message.reply(f"Произошла ошибка при обработке ссылки. Ошибка: {str(e)}")

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)