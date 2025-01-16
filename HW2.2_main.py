import os
from dotenv import load_dotenv
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart, Command
from aiogram.types import Message
from gtts import gTTS
from deep_translator import GoogleTranslator

# Загрузка переменных окружения из файла .env
load_dotenv()
API_TOKEN = os.getenv('TELEGRAM_API_TOKEN')

# Настройка логирования
logging.basicConfig(level=logging.INFO)

# Инициализация бота и диспетчера
bot = Bot(token=API_TOKEN)
dp = Dispatcher()


# Пример хендлера с использованием CommandStart
@dp.message(CommandStart())
async def start(message: Message):
    await message.answer(
        f"Привет {message.from_user.first_name}, напишите любой текст на русском, и я переведу его на английский и озвучу!")


# Пример хендлера с использованием Command
@dp.message(Command(commands=["help"]))
async def help_command(message: Message):
    await message.answer(
        "Этот бот умеет выполнять команды:\n/start\n/help\nПросто напишите любой текст на русском и я переведу его на английский и озвучу.")


# Хендлер для перевода и озвучки текста
@dp.message()
async def translate_and_speak(message: Message):
    # Перевод текста с русского на английский
    translated_text = GoogleTranslator(source='ru', target='en').translate(message.text)

    # Озвучка переведенного текста
    tts = gTTS(text=translated_text, lang='en')
    tts.save("translated_text.mp3")
    audio = types.FSInputFile("translated_text.mp3")

    # Отправка переведенного текста и аудио пользователю
    await message.answer(f"Перевод: {translated_text}")
    await bot.send_voice(chat_id=message.chat.id, voice=audio)

    # Удаление временного файла
    os.remove("translated_text.mp3")


async def main():
    dp.message.register(start, CommandStart())
    dp.message.register(help_command, Command(commands=["help"]))
    dp.message.register(translate_and_speak)

    await dp.start_polling(bot)


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
