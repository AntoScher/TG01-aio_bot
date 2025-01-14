import os
from dotenv import load_dotenv
import logging
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart, Command
from aiogram.handlers import MessageHandler
from aiogram.types import Message
import re
from pytube import YouTube

# Загрузка переменных окружения из файла .env
load_dotenv()

API_TOKEN = os.getenv('TELEGRAM_API_TOKEN')
YOUTUBE_API_KEY = os.getenv('YOUTUBE_API_KEY')

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
    await message.answer("Этот бот умеет выполнять команды:\n/start\n/help")


# Прописываем хендлер для команды /weather
@dp.message(lambda message: re.match(r'https?://(www\.)?youtube\.com/watch\?v=.+', message.text))
async def youtube_info(message: Message):
    url = message.text
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


async def main():
    dp.message.register(start, CommandStart())
    dp.message.register(help_command, Command(commands=["help"]))
    dp.message.register(youtube_info,
                        lambda message: re.match(r'https?://(www\.)?youtube\.com/watch\?v=.+', message.text))

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
