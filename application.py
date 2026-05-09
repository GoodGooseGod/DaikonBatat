import asyncio
import logging
from io import BytesIO
from typing import Callable

from bots.bot_manager import BotManager
from database.database_manager import DataBaseManager
from tasks_queue.task_manager import TaskManager


# Class for managing work of all application and managers
class Application:
    def __init__(self,
                 db_url: str,
                 tg_token: str,
                 vk_token: str,
                 vk_user_token: str = None,
                 ):
        # Creating managers
        self.db = DataBaseManager(db_url)
        self.bot = BotManager(self, tg_token, vk_token, vk_user_token)
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

    # Function for adding chat into chats database
    async def add_chat(self, chat_token: str, chat_id: int) -> bool:
        return await self.db.add_chat_token(chat_token, chat_id)

    # Function for selecting chats by user
    async def select_chat(self, user: int, chat_token: str) -> bool:
        return await self.db.add_users_chat(user, chat_token)

    # Function for deleting chats by user
    async def delete_chat(self, user: int, chat_token: str) -> bool:
        return await self.db.remove_users_chat(user, chat_token)

    # Function that returns all chats user selected
    async def show_selected_chats(self, user: int) -> list[str]:
        return await self.db.get_user_chats(user)

    # Function that takes another func, applies it to every user chat and returns success
    async def for_all_chats(self,
                            func: Callable,
                            user: int,
                            *args,
                            **kwargs
                            ) -> bool:
        success = True                                                  # Variable success for checking if all
        for chat_token in await self.db.get_user_chats(user):           # applies were successful.
            chat_id = await self.db.get_chat_id(chat_token)             # Getting chat id from database
            success = success and await func(chat_id, *args, **kwargs)  # Running func for every chat
        return success

    # Function for sending message into one chat by chat_id
    async def send_message_by_chat_id(self,
                                      chat_id: int = None,
                                      text: str = '',
                                      ) -> bool:
        return await self.bot.send_message(chat_id, text)

    # Function for sending message into all chats user selected
    async def send_message_by_user(self,
                                   text: str = '',
                                   user: int = None
                                   ) -> bool:
        return await self.for_all_chats(self.send_message_by_chat_id, user, text)

    # Function for sending photo by user
    async def send_photo(self, photo: BytesIO, user: int) -> bool:
        return await self.for_all_chats(self.bot.send_photo, user, photo)

    # Function for sending video by user
    async def send_video(self, video: BytesIO, user: int) -> bool:
        return await self.for_all_chats(self.bot.send_video, user, video)
