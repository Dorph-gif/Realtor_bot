import logging
import re
import os
from typing import Optional, List
from dotenv import load_dotenv
from io import BytesIO

from telethon import TelegramClient, events, Button

from src.bot_logic.state_machine import get_state_machine
from src.bot_logic.utils import is_admin, send_property_info
from src.bot_logic.database_service_client import get_database_service_client

load_dotenv()

LOG_FILE = os.path.join("logs", "bot.log")

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename=LOG_FILE,
)
logger = logging.getLogger(__name__)

class DeletePropertyHandler:
    def __init__(self, client: TelegramClient):
        self.client = client

    def register_handlers(self):
        self.client.add_event_handler(
            self.execute_delete,
            events.CallbackQuery(data=re.compile(r"^delete_property:(.*)$")),
        )

    async def execute_delete(self, event):
        user_id = event.sender_id
        property_id = int(event.data.decode().split(":")[1].strip())
        logger.info(f"User {user_id} started delete property process")
        database_client = get_database_service_client()
        try:
            await database_client.delete_property(property_id)
            await self.client.send_message(user_id, "Объявление удалено", buttons=[[Button.inline("В меню", "/start")]])
        except Exception as e:
            await self.client.send_message(user_id, "Произошла ошибка, попробуйте еще раз.")
            logger.exception(f"Delete property error: {e}")


        