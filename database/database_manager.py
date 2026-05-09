from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
import logging

from .models import Base
from .users_db import UsersDataBase
from .chats_db import ChatsDataBase


# Class for managing all databases
class DataBaseManager:
    def __init__(self, db_url: str):
        # Creating engine
        self.engine = create_async_engine(db_url)

        # Creating session maker
        self.session_maker = async_sessionmaker(
            bind=self.engine,
            expire_on_commit=False
        )

        # Creating table objects
        self.users = UsersDataBase(self.session_maker)
        self.chats = ChatsDataBase(self.session_maker)

    # Creating all tables
    async def create_tables(self) -> bool:
        try:
            async with self.engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
        except Exception as e:
            logging.exception(f'Error during creating tables: {e}')
            return False

    # Function for adding chat to user by his id and chat token
    async def add_users_chat(self, user_id: int, token: str) -> bool:
        try:
            await self.users.add_chat(user_id, token)
            return True
        except Exception as e:
            logging.exception(f'Error during adding chat to Users db: {e}')
            return False

    # Function for deleting chat from user by his id and chat token
    async def remove_users_chat(self, user_id: int, token: str) -> bool:
        try:
            await self.users.del_chat(user_id, token)
            return True
        except Exception as e:
            logging.exception(f'Error during deleting chat from Users db: {e}')
            return False

    # Function for getting all chats user selected
    async def get_user_chats(self, user_id: int) -> list[str]:
        try:
            return await self.users.get_chats(user_id)
        except Exception as e:
            logging.exception(f'Error during getting chat from Users db: {e}')
            return []

    # Function for adding chat to the database
    async def add_chat_token(self, token: str, chat_id: int) -> bool:
        try:
            await self.chats.add_chat(token, chat_id)
            return True
        except Exception as e:
            logging.exception(f'Error during adding chat to Chats db: {e}')
            return False

    # Function for deleting chat from the database
    async def remove_chat_token(self, token: str, chat_id: int) -> bool:
        try:
            await self.chats.del_chat(token, chat_id)
            return True
        except Exception as e:
            logging.exception(f'Error during deleting chat from Chats db: {e}')
            return False

    # Function for getting chat by chat token
    async def get_chat_id(self, token: str) -> int:
        try:
            return await self.chats.get_chat(token)
        except Exception as e:
            logging.exception(f'Error during getting chat from Chats db: {e}')
            return -1
