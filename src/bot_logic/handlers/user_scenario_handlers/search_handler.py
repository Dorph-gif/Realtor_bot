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

class SearchCommandHandler:
    def __init__(self, client: TelegramClient):
        self.client = client

    async def execute_choice(self, event):
        user_id = event.chat_id

        try:
            database_client = get_database_service_client()
            filter_list = await database_client.get_property_filters_list(user_id)

            message = "Выберите фильтр, по которому хотите начать поиск:"
            
            buttons = []

            for filter in filter_list:
                buttons.append([Button.inline(f"{filter['name']}", f"search:{filter['id']}")])

            buttons.append([Button.inline("В меню", "/start")])

            await self.client.send_message(event.chat_id, message, buttons=buttons)
        except Exception as e:
            await self.client.send_message(event.chat_id, "Произошла ошибка, попробуйте еще раз.")
            await go_to_neutral_state(event.chat_id, self.client)
            logger.exception(f"Delete filters from database error: {e}")

    async def execute_announcement(self, event):
        user_id = event.chat_id
        filter_id = int(event.data.decode().split(':')[1].strip())

        try:
            database_client = get_database_service_client()
            property_id = await database_client.get_next_announcement(filter_id)
            database_client.increase_statistics(property_id, "views")

            if not property_id:
                await self.client.send_message(event.chat_id, "Не найдено объявлений подходящих под параметры")
                await go_to_neutral_state(event.chat_id, self.client)
                return

            message = " . "

            buttons = [ 
                [Button.inline("Дальше 👉", f"search:{filter_id}")],
                [Button.inline("Связаться с риелтором 🤝", f"like:{filter_id}:{property_id}")],
                [Button.inline("В избранное ❤️", f"to_favorites:{property_id}")],
                [Button.inline("В меню", "/start")]
            ]

            await send_property_info(self.client, user_id, property_id, message, buttons=buttons)
        except Exception as e:
            await self.client.send_message(event.chat_id, "Произошла ошибка, попробуйте еще раз.")
            await go_to_neutral_state(event.chat_id, self.client)
            logger.exception(f"Delete filters from database error: {e}")

    async def execute_like(self, event):
        user_id = event.chat_id
        filter_id = event.data.decode().split(':')[1].strip()
        announcement_id = event.data.decode().split(':')[2].strip()

        try:
            database_client = get_database_service_client()
            announcement = await database_client.get_property_description(announcement_id)
            database_client.increase_statistics(announcement_id, "likes")

            if not announcement:
                await self.client.send_message(event.chat_id, "Ошибка отправки, попробуйте снова")
                await go_to_neutral_state(event.chat_id, self.client)
                return

            announcement_author = int(announcement["return_contact"])

            user_link = await get_user_link(self.client, user_id)
            rieltor_message = f"Пользователю {user_link} понравилось объявление {announcement_id}"
            rieltor_buttons = [
                [Button.inline("получить описание объявления", f"ad_description:{announcement_id}:{user_link}")]
            ]

            logger.info(f"sending notification contact: {announcement_author}")
            await self.client.send_message(announcement_author, message=rieltor_message, buttons=rieltor_buttons)

            user_message = "Уведомление отправлено, с вами свяжутся в ближайшее время!"

            user_buttons = []

            if filter_id != '-':
                user_buttons.append([Button.inline("Дальше 👉", f"search:{filter_id}")])

            user_buttons.append([Button.inline("В меню", "/start")])

            await self.client.send_message(user_id, message=user_message, buttons=user_buttons)
        except Exception as e:
            await self.client.send_message(event.chat_id, "Произошла ошибка, попробуйте еще раз.")
            await go_to_neutral_state(event.chat_id, self.client)
            logger.exception(f"Like error: {e}")

    async def execute_add_to_favorites(self, event):
        user_id = event.chat_id
        filter_name = event.data.decode().split(':')[1].strip()
        announcement_id = event.data.decode().split(':')[2].strip()

        try:
            database_client = get_database_service_client()
            await database_client.add_to_favorites(user_id, announcement_id)

            user_message = "Объявление добавлено в избранное!"
            user_buttons = [
                [Button.inline("Дальше 👉", f"search:{filter_name}")],
                [Button.inline("В меню", "/start")]
            ]

            await self.client.send_message(user_id, user_message, user_buttons)
        except Exception as e:
            await self.client.send_message(event.chat_id, "Произошла ошибка, попробуйте еще раз.")
            await go_to_neutral_state(event.chat_id, self.client)
            logger.exception(f"Add to favorites error: {e}")

    def register_handlers(self):
        self.client.add_event_handler(
            self.execute_choice,
            events.NewMessage(pattern="/search"),
        )
        self.client.add_event_handler(
            self.execute_choice,
            events.CallbackQuery(data="/search"),
        )
        self.client.add_event_handler(
            self.execute_announcement,
            events.CallbackQuery(data=re.compile(r"^search:(.*)$")),
        )
        self.client.add_event_handler(
            self.execute_like,
            events.CallbackQuery(data=re.compile(r"^like:(.*)$")),
        )