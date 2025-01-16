import os
from dotenv import load_dotenv
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart, Command
from aiogram.types import Message
import requests
import random
import aiohttp

# Загрузка переменных окружения из файла .env
load_dotenv()

API_TOKEN = os.getenv('TELEGRAM_API_TOKEN')
WEATHER_API_KEY = os.getenv('OPENWEATHERMAP_API_KEY')

# Настройка логирования
logging.basicConfig(level=logging.INFO)

# Инициализация бота и диспетчера
bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# Убедитесь, что папка 'img' существует
if not os.path.exists('img'):
    os.makedirs('img')


# Пример хендлера с использованием CommandStart
@dp.message(CommandStart())
async def start(message: Message):
    await message.answer(f"Привет {message.from_user.first_name}, я бот, который работает с фотографиями!")


# Пример хендлера с использованием Command
@dp.message(Command(commands=["help"]))
async def help_command(message: Message):
    await message.answer("Этот бот умеет выполнять команды:\n/start\n/help\n/photo")


@dp.message(Command(commands=["photo"]))
async def photo_command(message: Message):
    photos = [
        'https://img.freepik.com/free-photo/aerial-view-cityscape_181624-49144.jpg',
        'https://cdn2.tu-tu.ru/image/pagetree_node_data/1/5d6d5ea9f0b26d219a34767dea7b1140/'
    ]
    rand_photo = random.choice(photos)

    async with aiohttp.ClientSession() as session:
        async with session.get(rand_photo) as resp:
            if resp.status == 200:
                file_name = os.path.join('img', f"{os.path.basename(rand_photo)}.jpg")
                with open(file_name, 'wb') as f:
                    f.write(await resp.read())
                await message.answer_photo(photo=rand_photo, caption=f'Вот мой Минск. Фото сохранено как {file_name}')
            else:
                await message.reply("Не удалось загрузить фото.")


async def main():
    dp.message.register(start, CommandStart())
    dp.message.register(help_command, Command(commands=["help"]))
    dp.message.register(photo_command, Command(commands=["photo"]))

    await dp.start_polling(bot)


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
