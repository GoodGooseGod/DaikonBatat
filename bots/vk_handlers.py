from vkbottle.bot import Message as Message_vk, Bot as Bot_vk
from typing import NewType, Any
from config import DAIKON_BATAT_VK_ID

from secrets import token_urlsafe


BotManager = NewType('BotManager', Any)  # For typing


# Func creates vk bot and handlers for it.
def create_vk_bot(token: str, bot_manager: BotManager) -> Bot_vk:
    # Creating vk bot
    vk_bot = Bot_vk(token=token)

    # Handles inviting Daikon Batat to the chat and sends chat id
    @vk_bot.on.message()
    async def chat_join_handler(message: Message_vk) -> None:
        # Checking if messages is inviting and compares member_id to the Daikon Batat
        if message.action and message.action.type == 'chat_invite_user' and \
                abs(message.action.member_id) == DAIKON_BATAT_VK_ID:

            token = token_urlsafe(message.chat_id)
            await bot_manager.add_chat(token, message.chat_id)
            await message.answer('Дайкон батат. ' +
                                 f'\nВот id вашего чата: {token}' +
                                 '\nДобавьте его в рассылку при помощи команды select в телеграмм боте -> @DaikonBatatBOT' +
                                 '\nПример: /select 2')

    return vk_bot
