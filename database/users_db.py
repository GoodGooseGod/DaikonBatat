from sqlalchemy import select, insert, delete, Insert, Delete

from .models import DataBaseInterface, execute_scalars, execute_and_commit, Users


# Class for managing Users database
class UsersDataBase(DataBaseInterface):
    def __init__(self, session_maker):
        self.session_maker = session_maker

    # Adding chat to user by his id and chat token
    @execute_and_commit
    def add_chat(self, user_id: int, token: str) -> Insert:
        return insert(Users).values(id=user_id, token=token)

    # Deleting chat from user by his id and chat token
    @execute_and_commit
    def del_chat(self, user_id: int, token: str) -> Delete:
        return delete(Users).where(Users.id == user_id, Users.token == token)

    # Returning all chats user selected
    @execute_scalars
    def get_chats(self, user_id: int) -> list[str]:
        return select(Users.token).where(Users.id == user_id)