import os
from dotenv import load_dotenv
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
import requests
from urllib.parse import urlparse, unquote

# Загрузка переменных окружения из файла .env
load_dotenv()
API_TOKEN = os.getenv('TELEGRAM_API_TOKEN')
UNSPLASH_ACCESS_KEY = os.getenv('UNSPLASH_ACCESS_KEY')

# Настройка логирования
logging.basicConfig(level=logging.INFO)

# Инициализация бота и диспетчера
bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# Убедитесь, что папка 'img' существует
if not os.path.exists('img'):
    os.makedirs('img')

# Глобальный словарь для хранения URL фотографий
photo_urls = {}

# Клавиатура для выбора действия
def get_action_keyboard(sent_message_id):
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Загрузить фото", callback_data=f"upload_photo|{sent_message_id}")],
            [InlineKeyboardButton(text="Продолжить поиск", callback_data="continue_search")]
        ]
    )
    return keyboard

# Хендлер для команды /start
@dp.message(CommandStart())
async def start(message: Message):
    await message.answer("Привет! Напишите запрос на русском языке, и я найду подходящие фото на Unsplash.")

# Хендлер для обработки текстовых сообщений (поисковые запросы)
@dp.message()
async def search_photos(message: Message):
    query = message.text
    await message.answer(f"Ищу фото по запросу: {query}...")

    url = "https://api.unsplash.com/search/photos"
    headers = {"Authorization": f"Client-ID {UNSPLASH_ACCESS_KEY}"}
    params = {"query": query, "per_page": 3}  # Количество результатов

    response = requests.get(url, headers=headers, params=params)
    data = response.json()

    if data["total"] == 0:
        await message.answer("Не найдено подходящих фото. Пожалуйста, уточните запрос.")
        return

    for photo in data["results"]:
        photo_url = photo["urls"]["regular"]
        sent_message = await message.answer_photo(photo=photo_url, caption="Подходит это фото?", reply_markup=get_action_keyboard(photo["id"]))
        # Сохраняем URL фото в глобальный словарь
        logging.info(f"Сохраняем URL фото: {photo_url} для photo_id: {photo['id']}")
        photo_urls[photo["id"]] = photo_url

    await message.answer("Если нужно уточнить запрос, напишите его заново.")

# Хендлер для обработки нажатий на кнопки
@dp.callback_query()
async def handle_callbacks(query: CallbackQuery):
    callback_data = query.data

    if callback_data.startswith("upload_photo"):
        photo_id = callback_data.split("|")[1]
        photo_url = photo_urls.get(photo_id)

        logging.info(f"Получаем URL фото для photo_id: {photo_id} -> {photo_url}")

        if photo_url:
            await bot.send_message(query.message.chat.id, "Фото будет загружено на сервер в папку img.")
            response = requests.get(photo_url)
            if response.status_code == 200:
                # Извлечение имени файла из URL
                parsed_url = urlparse(photo_url)
                file_name = os.path.basename(parsed_url.path)
                file_name = unquote(file_name)  # Декодирование URL
                file_path = os.path.join('img', file_name)
                # Добавление расширения .jpg, если его нет
                if not file_path.endswith('.jpg'):
                    file_path += '.jpg'
                with open(file_path, 'wb') as f:
                    f.write(response.content)
                await bot.send_message(query.message.chat.id, f"Фото загружено как {file_path}")
            else:
                await bot.send_message(query.message.chat.id, "Не удалось загрузить фото.")
        else:
            await bot.send_message(query.message.chat.id, "Не удалось найти фото для загрузки.")

    elif callback_data == "continue_search":
        await bot.send_message(query.message.chat.id, "Пожалуйста, напишите новый поисковый запрос.")

async def main():
    dp.message.register(start, CommandStart())
    dp.message.register(search_photos)
    dp.callback_query.register(handle_callbacks)

    await dp.start_polling(bot)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
