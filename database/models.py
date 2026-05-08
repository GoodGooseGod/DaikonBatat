from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import ForeignKey
from sqlalchemy.ext.asyncio import async_sessionmaker
from typing import Callable, Protocol
from functools import wraps


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


class DataBaseInterface(Protocol):
    session_maker: async_sessionmaker


class Base(DeclarativeBase):
    pass


class Users(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(primary_key=True)
    token: Mapped[str] = mapped_column(
        ForeignKey("chats.token", ondelete="CASCADE"),
        primary_key=True
    )


class Chats(Base):
    __tablename__ = 'chats'

    token: Mapped[str] = mapped_column(primary_key=True)
    id: Mapped[int] = mapped_column(unique=True)