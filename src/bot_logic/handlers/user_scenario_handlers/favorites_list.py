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

LOG_FILE = os.path.join("logs", "bot.log")

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename=LOG_FILE,
)
logger = logging.getLogger(__name__)

class FavoritesListHandler:
    def __init__(self, client: TelegramClient):
        self.client = client

    def register_handlers(self):
        self.client.add_event_handler(
            self.execute_start,
            events.NewMessage(pattern=re.compile(r"^/favorites_list:(.*)$")),
        )
        self.client.add_event_handler(
            self.execute_start,
            events.CallbackQuery(data=re.compile(r"^/favorites_list:(.*)$")),
        )
        self.client.add_event_handler(
            self.show_property,
            events.CallbackQuery(data=re.compile(r"^show_favorites_property:(.*)$")),
        )

    async def execute_start(self, event):
        user_id = event.sender_id
        offset = int(event.data.decode().split(":")[1].strip())

        logger.info(f"User {user_id} started show favorites process")
        database_client = get_database_service_client()
        properties = await database_client.get_favorites_list(user_id, offset, limit=10)

        photos = []
        buttons = []

        if len(properties) == 0:
            await self.client.send_message(user_id, "Нет объектов для отображения.")
            return

        for property in properties:
            property_id = property["property_id"]
            favorite_id = property["id"]
            photo_bytes = await database_client.get_property_photo(property_id)

            photo = await self.client.upload_file(
                file=photo_bytes,
                file_name="photo.jpg",
            )

            photos.append(photo)
            buttons.append([Button.inline(f"Объект {property_id}", f"show_favorites_property:{property_id}:{favorite_id}")])

        buttons.append([Button.inline("Следующие 👉", f"favorites_list:{offset+10}")])
        buttons.append([Button.inline("В меню", "/start")])
        
        await self.client.send_file(user_id, photos)

        await self.client.send_message(user_id, message=" . ", buttons=buttons)

    async def show_property(self, event):
        user_id = event.sender_id
        property_id = int(event.data.decode().split(":")[1].strip())
        favorite_id = int(event.data.decode().split(":")[2].strip())

        buttons = [
            [Button.inline("Связаться с риелтором 🤝", f"like:-:{property_id}")],
            [Button.inline("Удалить из избранного", f"delete_from_favorites:{favorite_id}")],
            [Button.inline("В меню", "/start")]
        ]
        logger.info(f"User {user_id} requested property {property_id}")
        await send_property_info(self.client, user_id, property_id, is_admin=True, buttons=buttons)

