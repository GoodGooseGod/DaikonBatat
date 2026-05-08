from aiogram import Dispatcher, F, Bot as Bot_tg
from aiogram.filters import CommandStart, Command
from aiogram.types import Message as Message_tg
from typing import NewType, Any
import io

BotManager = NewType('BotManager', Any)  # For typing


# Func creates telegram bot and handlers for it.
def create_tg_bot(token: str, bot_manager: BotManager) -> (Bot_tg, Dispatcher):
    # Creating bot and dispatcher for handling messages
    tg_bot = Bot_tg(token)
    dp = Dispatcher()

    @dp.message(CommandStart())
    async def command_start(message: Message_tg):
        await message.answer('Привет, я Дайкон Батат - бот для пересылки сообщений и медиа из Телеграмм в Вк.\n' +
                             'Добавь меня в беседу Вк и вставь id беседы после добавления через команду /select.')

    # Handles command '/select' for selecting chat you want to send message
    @dp.message(Command('select'))
    async def command_select(message: Message_tg):
        chat = message.text.replace('/select', '').replace(' ', '')
        success = await bot_manager.select_chat(message.from_user.id, chat)

        if success:
            await message.answer(f'Чат {chat} были успешно выбраны.')
        else:
            await message.answer(f'Ошибка выбора чатов.')

    # Handles command '/delete' for removing chats from the list
    @dp.message(Command('delete'))
    async def command_delete_selection(message: Message_tg):
        chat = message.text.replace('/delete', '').replace(' ', '')
        success = await bot_manager.delete_chat(message.from_user.id, chat)

        if success:
            await message.answer(f'Чат {chat} был успешно удалён из рассылки.')
        else:
            await message.answer(f'Ошибка удаления чатов.')

    @dp.message(Command('show_chats'))
    async def command_select(message: Message_tg):
        success = await bot_manager.show_selected_chats()

        if success:
            await message.answer(f'Ваши выбранные чаты: {success}.')
        else:
            await message.answer(f'Ошибка отображения чатов.')

    # Handles command '/text' for sending simple messages to the chat
    @dp.message(Command('text'))
    async def command_text(message: Message_tg):
        success = await bot_manager.send_message_by_user(message.text.replace('/text ', ''), user=message.from_user.id)

        if success:
            await message.reply(f'Сообщение было успешно отправлено.')
        else:
            await message.reply(f'Ошибка отправки сообщения.')

    # Handles commands '/' or '/resend' for sending replying message one more time
    @dp.message(Command('', 'resend'))
    async def command_resend(message: Message_tg):
        message = message.reply_to_message
        if message.photo:                                               # Calls photo handler
            await handle_photo(message)
        elif message.video or message.animation or message.document:    # Calls media handler
            await handle_media(message)
        else:                                                           # Calls simple message handler
            await command_text(message)

    # Handles photos for sending them to the chat
    @dp.message(F.photo)
    async def handle_photo(message: Message_tg):
        await message.reply('Фото обрабатывается, оно будет отправлено в ближайшее время.')

        # Downloading photo from telegram
        file_info = await tg_bot.get_file(message.photo[-1].file_id)
        file_bytes_io = await tg_bot.download_file(file_path=file_info.file_path)

        # Preparing photo to sending
        photo = io.BytesIO(file_bytes_io.getvalue())
        photo.name = f"{message.photo[-1].file_id}.jpg"
        # Sending and checking exception status
        success = await bot_manager.send_photo(photo, message.from_user.id)

        if success:
            await message.reply('Фото успешно отправлено')
        else:
            await message.reply('Ошибка при отправке фото в ВК')
        return success

    # Handles videos, gifs, animated stickers for sending them to the chat
    @dp.message(F.video | F.animation | F.document)
    async def handle_media(message: Message_tg):
        await message.reply('Видео обрабатывается, оно будет отправлено в ближайшее время.')

        # Downloading video from telegram
        file = message.video or message.animation or message.document
        file_info = await tg_bot.get_file(file.file_id)
        file_bytes_io = await tg_bot.download_file(file_info.file_path)

        # Preparing video to sending
        video = io.BytesIO(file_bytes_io.getvalue())
        video.name = file.file_name or f"{file.file_id}.mp4"
        # Sending and checking exception status
        success = await bot_manager.send_video(video, message.from_user.id)

        if success:
            await message.reply('Видео успешно отправлено')
        else:
            await message.reply('Ошибка при отправке медиа в ВК')
        return success

    return tg_bot, dp
