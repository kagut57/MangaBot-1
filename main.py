import asyncio as aio

from api import run_web_server
from bot import bot, DB, manga_updater, chapter_creation


async def async_main():
    db = DB()
    await db.connect()
    await run_web_server()
    
if __name__ == '__main__':
    loop = aio.get_event_loop_policy().get_event_loop()
    loop.run_until_complete(async_main())
    loop.create_task(manga_updater())
    for i in range(10):
        loop.create_task(chapter_creation(i + 1))
    bot.run()
