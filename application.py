from secrets import token_urlsafe
import asyncio
import logging

from bots.bot_manager import BotManager
from database.database_manager import DataBaseManager
from tasks_queue.task_manager import TaskManager


# Class for managing work of all application
class Application:
    def __init__(self,
                 db_url: str,
                 tg_token: str,
                 vk_token: str,
                 vk_user_token: str = None,
                 ):
        # Creating managers
        self.db = DataBaseManager(db_url)
        self.bot = BotManager(self.db, tg_token, vk_token, vk_user_token)
        self.queue = TaskManager()

    # Main function. Starts application work
    async def start(self):
        try:
            await self.bot.tg_bot.delete_webhook(drop_pending_updates=True)         # Deleting webhooks
            await self.db.create_tables()                                           # Creating database tables

            logging.info("Running bots...")
            await asyncio.gather(                                                   # Creating async coroutines
                self.bot.dp.start_polling(self.bot.tg_bot, handle_signals=False),   # Starting telegram bot
                self.bot.start_vk()                                                 # Starting vk bot
            )
        finally:  # If exception - closing bots.
            await self.bot.tg_bot.session.close()
            await self.bot.vk_bot.api.http_client.close()
