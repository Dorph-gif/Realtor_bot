from telethon import TelegramClient
from telethon.events import NewMessage
from telethon import TelegramClient, events, Button
import logging
import os
import re

from src.bot_logic.utils import go_to_neutral_state
from src.bot_logic.database_service_client import get_database_service_client

LOG_FILE = os.path.join("logs", "bot.log")

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename=LOG_FILE,
)
logger = logging.getLogger(__name__)

class ListCommandHandler:
    def __init__(self, client: TelegramClient):
        self.client = client

    async def execute(self, event):
        user_id = event.chat_id

        try:
            database_client = get_database_service_client()
            filter_list = await database_client.get_property_filters_list(user_id)

            message = "Вот список ваших фильтров: \n"
            for filter in filter_list:
                message += filter["name"] + "\n"

            await self.client.send_message(event.chat_id, message)
            await go_to_neutral_state(event.chat_id, self.client)
        except Exception as e:
            await self.client.send_message(event.chat_id, "Произошла ошибка, попробуйте еще раз.")
            logger.exception(f"Get list filters from database error: {e}")

    def register_handlers(self):
        self.client.add_event_handler(
            self.execute,
            events.NewMessage(pattern="/filters_list"),
        )
        self.client.add_event_handler(
            self.execute,
            events.CallbackQuery(data="/filters_list"),
        )