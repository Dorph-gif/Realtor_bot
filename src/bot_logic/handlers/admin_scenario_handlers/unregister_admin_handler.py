from telethon import TelegramClient
from telethon.events import NewMessage
from telethon import TelegramClient, events, Button
import logging
import os

from dotenv import load_dotenv
load_dotenv()

from src.bot_logic.utils import go_to_neutral_state
from src.bot_logic.database_service_client import get_database_service_client

LOG_FILE = os.path.join("logs", "bot.log")

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename=LOG_FILE,
)
logger = logging.getLogger(__name__)

class UnregisterAdminCommandHandler:
    def __init__(self, client: TelegramClient):
        self.client = client

    async def execute(self, event):
        user_id = event.chat_id

        try:
            database_client = get_database_service_client()
            await database_client.unregister_admin(user_id)

            await self.client.send_message(event.chat_id, "Вы больше не администратор.")
            await go_to_neutral_state(event.chat_id, self.client)
        except Exception as e:
            await self.client.send_message(event.chat_id, "Произошла ошибка, попробуйте еще раз.")
            logger.exception(f"Unregister admin error: {e}")

    def register_handlers(self):
        self.client.add_event_handler(
            self.execute,
            events.CallbackQuery(data="/unregister_admin"),
        )