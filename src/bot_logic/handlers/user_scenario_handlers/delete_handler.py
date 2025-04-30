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

class DeleteCommandHandler:
    def __init__(self, client: TelegramClient):
        self.client = client

    async def execute_choice(self, event):
        user_id = event.chat_id

        try:
            database_client = get_database_service_client()
            filter_list = await database_client.get_property_filters_list(user_id)
            logger.info(f"User {user_id}: получен список фильтров для удаления: {filter_list}")

            message = "Выберите фильтр для удаления:"
            
            buttons = []

            for filter in filter_list:
                filter_name= filter['name']
                filter_id= filter['id']
                buttons.append([Button.inline(f"{filter_name}", f"delete:{filter_id}")])
            
            buttons.append([Button.inline("В меню", "/start")])

            await self.client.send_message(event.chat_id, message, buttons=buttons)
        except Exception as e:
            await self.client.send_message(event.chat_id, "Произошла ошибка, попробуйте еще раз.")
            logger.exception(f"Delete filters from database error: {e}")

    async def execute_delete(self, event):
        user_id = event.chat_id
        filter_id = event.data.decode().split(':')[1].strip()

        try:
            database_client = get_database_service_client()
            await database_client.delete_property_filter(user_id, filter_id)

            message = "Фильтр успешно удален!"

            await self.client.send_message(event.chat_id, message)
            await go_to_neutral_state(event.chat_id, self.client)
        except Exception as e:
            await self.client.send_message(event.chat_id, "Произошла ошибка, попробуйте еще раз.")
            logger.exception(f"Delete filters from database error: {e}")

    def register_handlers(self):
        self.client.add_event_handler(
            self.execute_choice,
            events.NewMessage(pattern="/delete_filter"),
        )
        self.client.add_event_handler(
            self.execute_choice,
            events.CallbackQuery(data="/delete_filter"),
        )
        self.client.add_event_handler(
            self.execute_delete,
            events.CallbackQuery(data=re.compile(r"^delete:(.*)$")),
        )