from sqlalchemy import select, insert, delete, Insert, Delete

from .models import DataBaseInterface, execute_one_scalar, execute_and_commit, Chats


# Class for managing Chats database
class ChatsDataBase(DataBaseInterface):
    def __init__(self, session_maker):
        self.session_maker = session_maker

    # Adding chat to the database
    @execute_and_commit
    def add_chat(self, token: str, chat_id: int) -> Insert:
        return insert(Chats).values(token=token, id=chat_id)

    # Deleting chat from the database
    @execute_and_commit
    def del_chat(self, token: str) -> Delete:
        return delete(Chats).where(Chats.token == token)

    # Selecting chat by chat token
    @execute_one_scalar
    def get_chat(self, token: str) -> int | None:
        return select(Chats.id).where(Chats.token == token)