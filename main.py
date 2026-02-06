from os import getenv
import asyncio
from aiogram import Bot, Dispatcher
from dotenv import load_dotenv
load_dotenv()
from handlers.routes import router
from database import init_db, create_test_tournaments



TOKEN = getenv("BOT_TOKEN")

dp = Dispatcher()
dp.include_router(router)

async def main():
    bot = Bot(token=TOKEN)
    init_db()
#    create_test_tournaments()  #Если активна, то при каждом перезапуске бота будет удалять турниры и создавать тестовые заново.


    print("Start..")
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
