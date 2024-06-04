from aiogram import Bot, Dispatcher, executor
from config import TOKEN

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

if __name__ == '__main__':
    executor.start_polling(dp)