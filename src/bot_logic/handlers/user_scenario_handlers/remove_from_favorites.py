from telethon import TelegramClient
from telethon.events import NewMessage
from telethon import TelegramClient, events, Button
import logging
import os
import re

from src.bot_logic.utils import go_to_neutral_state, send_property_info, get_user_link
from src.bot_logic.database_service_client import get_database_service_client

LOG_FILE = os.path.join("logs", "bot.log")

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename=LOG_FILE,
)
logger = logging.getLogger(__name__)

class DeleteFromFavoritesCommandHandler:
    def __init__(self, client: TelegramClient):
        self.client = client

    async def execute(self, event):
        user_id = event.chat_id
        favorites_id = event.data.decode().split(":")[1].strip()

        try:
            database_client = get_database_service_client()

            message = "Удалено!"
            
            buttons = [[Button.inline("В меню", "/start")]]

            await database_client.delete_from_favorites(favorites_id)

            await self.client.send_message(event.chat_id, message, buttons=buttons)
        except Exception as e:
            await self.client.send_message(event.chat_id, "Произошла ошибка, попробуйте еще раз.")
            await go_to_neutral_state(event.chat_id, self.client)
            logger.exception(f"Delete from favorites error: {e}")

    def register_handlers(self):
        self.client.add_event_handler(
            self.execute,
            events.CallbackQuery(data=re.compile(r"^delete_from_favorites:(.*)$")),
        )
