from random import randint
from vkbottle import API, PhotoMessageUploader, VideoUploader
from io import BytesIO
import logging

from bots.telegram_handlers import *
from bots.vk_handlers import *
from database.database_manager import DataBaseManager
from config import VK_CHAT_PEER_OFFSET


# Class for managing both tg and vk bots.
class BotManager:
    def __init__(self,
                 data_base: DataBaseManager,
                 tg_token: str,
                 vk_token: str,
                 vk_user_token: str = None):
        # Creating bots and connecting database
        self.tg_bot, self.dp = create_tg_bot(tg_token, self)
        self.vk_bot = create_vk_bot(vk_token, self)
        self.db = data_base

        # User token using to sending videos by users name. Seems like bot can't send videos by itself.
        if vk_user_token:
            self.vk_user = API(vk_user_token)

    # Starting VK-bot by hand-made func because built-in refused to work with telegram bot at the same time.
    async def start_vk(self) -> None:
        logging.info("VK-bot has started working")
        async for event in self.vk_bot.polling.listen():
            for update in event.get("updates", []):
                await self.vk_bot.router.route(update, self.vk_bot.api)

    async def add_chat(self, token: str, chat_id: int) -> bool:
        try:
            await self.db.add_chat_token(token, chat_id)
        except Exception as e:
            logging.error(f'Error during adding chat: {e}')
            return False
        logging.info(f'Added chat.')
        return True

    # Function for selecting chats by user
    async def select_chat(self, user: int, token: str) -> bool:
        try:
            await self.db.add_users_chat(user, token)
        except Exception as e:
            logging.error(f'Error during selecting chat: {e}')
            return False
        logging.info(f'Selected chats for user={user}.')
        return True

    # Function for deleting chats by user
    async def delete_chat(self, user: int, token: str) -> bool:
        try:
            await self.db.remove_users_chat(user, token)

        except Exception as e:
            logging.error(f'Error during deleting chat: {e}')
            return False
        logging.info(f'Successful undo selection chat {token}.')
        return True

    async def show_selected_chats(self, user: int) -> list[str] | bool:
        try:
            return await self.db.get_user_chats(user)
        except Exception as e:
            logging.error(f'Error during showing selected chats: {e}')
            return False

    # Function for sending message into one chat by chat_id
    async def send_message_by_chat_id(self,
                                      text: str = '',
                                      attachment: str | list[str] = None,
                                      token: str = None,
                                      chat_id: int = None,
                                      ) -> bool:
        try:
            chat_id = chat_id or await self.db.get_chat_id(token)
            await self.vk_bot.api.messages.send(
                chat_id=chat_id,
                message=text,
                random_id=randint(1, 2 ** 31),
                attachment=attachment,
            )
        except Exception as e:
            logging.error(f'Error during sending message: {e}')
            return False
        return True

    # Function for sending message into all chats user selected
    async def send_message_by_user(self,
                                   text: str = '',
                                   attachment: str | list[str] = None,
                                   user: int = None
                                   ) -> bool:
        success = True
        try:
            for token in await self.db.get_user_chats(user):
                success &= await self.send_message_by_chat_id(text, token=token, attachment=attachment)
        except Exception as e:
            logging.error(f'Error during sending message: {e}')
            return False
        return success

    # Function for sending photo by user
    async def send_photo(self, photo: BytesIO, user: int) -> bool:
        success = True
        try:
            # Couldn't use send_message_by_user because photo needs peer_id depending on chat_id
            for token in await self.db.get_user_chats(user):
                chat_id = await self.db.get_chat_id(token)
                # Uploading photo in vk
                attachment = await PhotoMessageUploader(self.vk_bot.api).upload(
                    file_source=photo,
                    peer_id=VK_CHAT_PEER_OFFSET + chat_id
                )

                success &= await self.send_message_by_chat_id(chat_id=chat_id, attachment=attachment)

        except Exception as e:
            logging.error(f'Error during sending photo: {e}')
            return False
        return success

    # Function for sending video by user. Parameter "is_round" defines if video will be circle or not.
    async def send_video(self, video: BytesIO, user: int) -> bool:
        try:
            # Uploading video in vk
            video_data = await VideoUploader(self.vk_user).upload(
                file_source=video,
                name=video.name,
                description="",
                is_private=True,
            )
            success = await self.send_message_by_user(user=user, attachment=video_data)

        except Exception as e:
            logging.error(f'Error during sending video: {e}')
            return False
        return success
