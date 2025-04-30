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

class ShowPropertiesHandler:
    def __init__(self, client: TelegramClient):
        self.client = client

    def register_handlers(self):
        self.client.add_event_handler(
            self.execute_start,
            events.NewMessage(pattern=re.compile(r"^show_properties:(.*)$")),
        )
        self.client.add_event_handler(
            self.execute_start,
            events.CallbackQuery(data=re.compile(r"^show_properties:(.*)$")),
        )
        self.client.add_event_handler(
            self.show_property,
            events.CallbackQuery(data=re.compile(r"^show_property:(.*)$")),
        )

    async def execute_start(self, event):
        user_id = event.sender_id
        offset = int(event.data.decode().split(":")[1].strip())

        if not await is_admin(self.client, user_id):
            await self.client.send_message(user_id, "У вас нет прав на эту команду.")
            return

        logger.info(f"User {user_id} started show properties process")
        database_client = get_database_service_client()
        properties_id = await database_client.get_property_list(offset, limit=10)

        logger.info(f"Properties list for user {user_id}: {properties_id}")

        properties_id = properties_id["properties"]

        photos = []
        buttons = []

        if len(properties_id) == 0:
            await self.client.send_message(user_id, "Нет объектов для отображения.")
            return

        for property_id in properties_id:
            property_id = property_id["id"]
            photo_bytes = await database_client.get_property_photo(property_id)

            photo = await self.client.upload_file(
                file=photo_bytes,
                file_name="photo.jpg",
            )

            photos.append(photo)
            buttons.append([Button.inline(f"Объект {property_id}", f"show_property:{property_id}")])

        buttons.append([Button.inline("Следующие 👉", f"show_properties:{offset+10}")])
        buttons.append([Button.inline("В меню", "/start")])

        logger.info(f"Sending message with buttons {buttons}")
        
        await self.client.send_file(user_id, photos)

        await self.client.send_message(user_id, message=" . ", buttons=buttons)
        logger.info(f"Message with photos sent to {user_id}")

    async def show_property(self, event):
        user_id = event.sender_id
        property_id = int(event.data.decode().split(":")[1].strip())
        buttons = [
            [Button.inline("Получить статистику", f"get_property_statistics:{property_id}"), 
             Button.inline("Снова активно", f"property_back_active:{property_id}")],
            [Button.inline("В аренде", f"become_rented_property:{property_id}"),
            Button.inline("Продано", f"sold_property:{property_id}")],
            [Button.inline("Удалить", f"delete_property:{property_id}"),
            Button.inline("В меню", "/start")]
        ]
        logger.info(f"User {user_id} requested property {property_id}")
        await send_property_info(self.client, user_id, property_id, is_admin=True, buttons=buttons)

