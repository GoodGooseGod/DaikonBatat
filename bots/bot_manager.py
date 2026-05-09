import logging
from vkbottle import API, PhotoMessageUploader, VideoUploader
from io import BytesIO
from random import randint

from config import VK_CHAT_PEER_OFFSET
from bots.telegram_handlers import *
from bots.vk_handlers import *


# Class for managing both tg and vk bots
class BotManager:
    def __init__(self,
                 app: Application,
                 tg_token: str,
                 vk_token: str,
                 vk_user_token: str = None,
                 ):
        # Creating bots
        self.tg_bot, self.dp = create_tg_bot(tg_token, app)
        self.vk_bot = create_vk_bot(vk_token, app)

        # User token using to sending videos by users name. Seems like bot can't send videos by itself
        if vk_user_token:
            self.vk_user = API(vk_user_token)

    # Starting VK-bot by hand-made func because built-in refused to work with telegram bot at the same time
    async def start_vk(self) -> None:
        logging.info("VK-bot has started working")
        async for event in self.vk_bot.polling.listen():
            for update in event.get("updates", []):
                await self.vk_bot.router.route(update, self.vk_bot.api)

    # Function for sending message into vk chat with text and attachment
    async def send_message(self,
                           chat_id: int,
                           text: str = '',
                           attachment: str | list[str] = None,
                           ) -> bool:
        try:
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

    # Function for sending photo into vk chat
    async def send_photo(self,
                         chat_id: int,
                         photo: BytesIO,
                         ) -> bool:
        try:
            # Uploading photo in vk
            photo_data = await PhotoMessageUploader(self.vk_bot.api).upload(
                file_source=photo,
                peer_id=VK_CHAT_PEER_OFFSET + chat_id
            )

            success = await self.send_message(chat_id, attachment=photo_data)
            return success

        except Exception as e:
            logging.error(f'Error during sending photo: {e}')
            return False

    # Function for sending video into vk chat
    async def send_video(self,
                         chat_id: int,
                         video: BytesIO,
                         ) -> bool:
        try:
            # Uploading video in vk
            video_data = await VideoUploader(self.vk_user).upload(
                file_source=video,
                name=video.name,
                description="",
                is_private=True,
            )

            success = await self.send_message(chat_id, attachment=video_data)
            return success

        except Exception as e:
            logging.error(f'Error during sending photo: {e}')
            return False
