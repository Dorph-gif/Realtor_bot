import logging
import re
import os
from typing import Optional, List
from dotenv import load_dotenv
from io import BytesIO

from telethon import TelegramClient, events, Button
from telethon.types import InputMediaPhoto
from telethon.types import MessageMediaPhoto
from telethon.types import MessageMediaDocument

from src.bot_logic.state_machine import get_state_machine
from src.bot_logic.utils import is_admin, send_property_info
from src.bot_logic.database_service_client import get_database_service_client

load_dotenv()

LOG_FILE = os.path.join("logs", "add_property.log")

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename=LOG_FILE,
)
logger = logging.getLogger(__name__)

class SoldRentedFreePropertyHandler:
    def __init__(self, client: TelegramClient):
        self.client = client

    def register_handlers(self):
        self.client.add_event_handler(
            self.execute,
            events.CallbackQuery(data=re.compile(r"^become_rented_property:(.*)$")),
        )
        self.client.add_event_handler(
            self.execute,
            events.CallbackQuery(data=re.compile(r"^sold_property:(.*)$")),
        )        
        self.client.add_event_handler(
            self.execute,
            events.CallbackQuery(data=re.compile(r"^property_back_active:(.*)$")),
        )

    async def execute(self, event):
        user_id = event.sender_id

        text  = event.data.decode().split(":")[0].strip()
        property_id  = event.data.decode().split(":")[1].strip()

        new_state = "Активно"

        if text == "sold_property":
            new_state = "Продано"
        elif text == "become_rented_property":
            new_state = "В аренде"

        buttons=[
            [Button.inline("Назад", f"show_property:{property_id}")],
            [Button.inline("В меню", "/start")]
        ]   

        if not await is_admin(self.client, user_id):
            await self.client.send_message(user_id, "У вас нет прав на эту команду.", buttons=[[Button.inline("В меню", "/start")]])
            return

        try:
            database_client = get_database_service_client()

            await database_client.change_property_state(property_id, new_state)
            
            await self.client.send_message(user_id, message="Готово!", buttons=buttons)
        except Exception as e:
            await self.client.send_message(user_id, message="Произошла ошибка, попробуйте снова!", buttons=[[Button.inline("В меню", "/start")]])

            logger.warning("Change property state error: %s", e)
