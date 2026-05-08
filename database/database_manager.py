from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
import logging

from .models import Base
from .users_db import UsersDataBase
from .chats_db import ChatsDataBase


class DataBaseManager:
    def __init__(self, db_url: str):
        self.engine = create_async_engine(db_url)

        self.session_maker = async_sessionmaker(
            bind=self.engine,
            expire_on_commit=False
        )

        self.users = UsersDataBase(self.session_maker)
        self.chats = ChatsDataBase(self.session_maker)

    async def create_tables(self):
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    async def add_users_chat(self, user_id: int, token: str) -> bool:
        try:
            await self.users.add_chat(user_id, token)
            return True
        except Exception as e:
            logging.exception(f'Error during adding chat to Users db: {e}')
            return False

    async def remove_users_chat(self, user_id: int, token: str) -> bool:
        try:
            await self.users.del_chat(user_id, token)
            return True
        except Exception as e:
            logging.exception(f'Error during deleting chat from Users db: {e}')
            return False

    async def get_user_chats(self, user_id: int) -> list[str]:
        try:
            return await self.users.get_chats(user_id)
        except Exception as e:
            logging.exception(f'Error during getting chat from Users db: {e}')
            return []

    async def add_chat_token(self, token: str, chat_id: int) -> bool:
        try:
            await self.chats.add_chat(token, chat_id)
            return True
        except Exception as e:
            logging.exception(f'Error during adding chat to Chats db: {e}')
            return False

    async def remove_chat_token(self, token: str, chat_id: int) -> bool:
        try:
            await self.chats.del_chat(token, chat_id)
            return True
        except Exception as e:
            logging.exception(f'Error during deleting chat from Chats db: {e}')
            return False

    async def get_chat_id(self, token: str) -> int:
        try:
            return await self.chats.get_chat(token)
        except Exception as e:
            logging.exception(f'Error during getting chat from Chats db: {e}')
            return -1

# async def check_user_exist(self, user_id: int) -> bool:
#     pass
#
# async def check_chat_token_exist(self, chat_token: str) -> bool:
#     pass
