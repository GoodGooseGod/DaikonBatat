import logging
import asyncio

from config import *
from application import Application


async def main():                       # Main func. Has 3 restarting attempts by default.
    restarts = 3
    while restarts > 0:
        try:                            # Starting app
            app = Application(DATABASE_URL, TELEGRAM_BOT_TOKEN, VK_BOT_TOKEN, VK_USER_TOKEN)
            await app.start()
        except KeyboardInterrupt:       # If program is closed.
            break
        except Exception as e:          # Exception catching and restarting.
            restarts -= 1
            logging.error(f"Exception: {e}")
            if restarts > 0:
                logging.info(f"Restart after 5 sec. Attempts remain: {restarts}")
                await asyncio.sleep(5)
    else:
        logging.error(f"Couldn't start bot. Shutting down.")


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.info('Keyboard Interruption')