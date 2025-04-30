from telethon import TelegramClient
from telethon.events import NewMessage
from telethon import TelegramClient, events, Button
import re

from src.bot_logic.utils import go_to_neutral_state, send_property_info

class AdDescriptionCommandHandler:
    def __init__(self, client: TelegramClient):
        self.client = client

    async def execute(self, event):
        announcement_id = event.data.decode().split(':')[1].strip()
        user_link = event.data.decode().split(':')[2].strip()

        message = f"Понравилось пользователю {user_link}"

        buttons = [
            [Button.inline("В меню", "/start")]
        ]

        await send_property_info(self.client, event.chat_id, announcement_id, message, buttons)

    def register_handlers(self):
        self.client.add_event_handler(
            self.execute,
            events.CallbackQuery(data=re.compile(r"^ad_description:(.*)$")),
        )