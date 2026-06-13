import asyncio
from aiogram import Bot, Dispatcher
from config import config
from handlers.start import main_router
from handlers.menu import menu_router
from handlers.cart import cart_router
from databases.init_db import Database
from databases.products import check_all_products

dp = Dispatcher()

async def update():
    asyncio.create_task(check_all_products())

async def main():
    bot = Bot(token=config.bot_token)

    dp.include_router(main_router)
    dp.include_router(menu_router)
    dp.include_router(cart_router)
    dp.startup.register(update)

    db = Database()
    await db.connect()

    if config.admin_id:
        try:
            await bot.send_message(chat_id=config.admin_id, text="Bot launched successfully!\n\n"
                                                                 "/start")
        except Exception as e:
            print(f"Failed to send startup message to admin: {e}")

    await dp.start_polling(bot, db=db)


if __name__ == '__main__':
    asyncio.run(main())
