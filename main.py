from os import getenv
import asyncio
from aiogram import Bot, Dispatcher
from dotenv import load_dotenv
from handlers.routes import router

# импорт для db от джемени
from database import init_db, create_test_tournaments

load_dotenv()
TOKEN = getenv("BOT_TOKEN")

dp = Dispatcher()
dp.include_router(router)


async def main():
    bot = Bot(token=TOKEN)
    init_db()
    create_test_tournaments()

    print("Start..")
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
