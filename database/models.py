from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import ForeignKey
from sqlalchemy.ext.asyncio import async_sessionmaker
from typing import Callable, Protocol
from functools import wraps


# Decorator that executes sql request and returns all scalars
def execute_scalars(func: Callable):
    @wraps(func)
    async def wrapper(self, *args, **kwargs):
        async with self.session_maker() as session:
            try:
                stmt = func(self, *args, **kwargs)
                result = await session.execute(stmt)
                return result.scalars().all()

            except Exception as e:
                raise Exception(f'Exception during SQL request: {e}')
    return wrapper


# Decorator that executes sql request and returns one scalar
def execute_one_scalar(func: Callable):
    @wraps(func)
    async def wrapper(self, *args, **kwargs):
        async with self.session_maker() as session:
            try:
                stmt = func(self, *args, **kwargs)
                result = await session.execute(stmt)
                return result.scalar_one_or_none()

            except Exception as e:
                raise Exception(f'Exception during SQL request: {e}')
    return wrapper


# Decorator that executes and commits sql request
def execute_and_commit(func: Callable):
    @wraps(func)
    async def wrapper(self, *args, **kwargs):
        async with self.session_maker() as session:
            try:
                stmt = func(self, *args, **kwargs)
                result = await session.execute(stmt)
                await session.commit()
                return result

            except Exception as e:
                await session.rollback()
                raise Exception(f'Exception during SQL request: {e}')
    return wrapper


# Interface for databases
class DataBaseInterface(Protocol):
    session_maker: async_sessionmaker


# Base from sqlalchemy for databases
class Base(DeclarativeBase):
    pass


# Users database with 2 columns: id, token
# Both primary keys, so one user can have many selected chats
class Users(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(primary_key=True)
    token: Mapped[str] = mapped_column(
        ForeignKey("chats.token", ondelete="CASCADE"),
        primary_key=True
    )


# Users database with 2 columns: token, id
# Chat token was made for safety and prevents selecting chats that aren't yours
class Chats(Base):
    __tablename__ = 'chats'

    token: Mapped[str] = mapped_column(primary_key=True)
    id: Mapped[int] = mapped_column(unique=True)