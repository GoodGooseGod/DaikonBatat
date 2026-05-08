# Reading file 'bot_token.txt' for tokens.
# If you want to try bot by yourself create this file and put required tokens in it by examples:
#       telegram: 1234
#       vk: vk1.a.1234
#       vk_user_token: 1234
#       db_url: postgresql+asyncpg://user:password@localhost/bot_db

with open('bot_token.txt', 'r') as file:
    TELEGRAM_BOT_TOKEN = file.readline().replace('telegram: ', '').replace('\n', '')
    VK_BOT_TOKEN = file.readline().replace('vk: ', '').replace('\n', '')
    VK_USER_TOKEN = file.readline().replace('vk_user_token: ', '').replace('\n', '')
    DATABASE_URL = file.readline().replace('db_url: ', '').replace('\n', '')


VK_CHAT_PEER_OFFSET = 2000000000
DAIKON_BATAT_VK_ID = 238010931
