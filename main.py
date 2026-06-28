import asyncio
import os

from aiohttp import web
from aiogram import Bot, Dispatcher

from config import config
from handlers import routers
from database import Database
from services.loader import check_all_products

dp = Dispatcher()


async def handle_ping(request):
    return web.Response(text="The Bot is working! Everything's great!", status=200)


async def start_web_server():
    app = web.Application()
    app.router.add_get("/", handle_ping)
    port = int(os.getenv("PORT", 8080))
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()
    print(f"Web-server started on port {port}")


async def main():
    await start_web_server()
    bot = Bot(token=config.bot_token)
    db = Database()
    await db.connect()

    for router in routers:
        dp.include_router(router)

    asyncio.create_task(check_all_products(db))

    if config.admin_id:
        try:
            await bot.send_message(chat_id=config.admin_id, text="Bot launched /start")
        except Exception as e:
            print(f"Failed to send startup message to admin: {e}")

    print("🤖 Bot started!")
    await dp.start_polling(bot, db=db)


if __name__ == '__main__':
    asyncio.run(main())
