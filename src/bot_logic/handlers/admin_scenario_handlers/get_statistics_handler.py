import logging
import re
import os
from dotenv import load_dotenv

from telethon import TelegramClient, events, Button

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

class GetStatisticsHandler:
    def __init__(self, client: TelegramClient):
        self.client = client

    def register_handlers(self):
        self.client.add_event_handler(
            self.execute,
            events.CallbackQuery(data="/get_statistics"),
        )

    async def execute(self, event):
        user_id = event.sender_id

        if not await is_admin(self.client, user_id):
            await self.client.send_message(user_id, "У вас нет прав на эту команду.")
            return

        try:
            database_client = get_database_service_client()
            statistic = await database_client.get_statistics()

            message = ""
            message += f"Просмотров: {statistic['views']}\n"
            message += f"В избранном: {statistic['favorites']}\n"
            message += f"Запросов на диалог с риэлтором: {statistic['likes']}\n"

            buttons=[
                [Button.inline("В меню", "/start")]
            ]   

            await self.client.send_message(user_id, message=message, buttons=buttons)
            logger.info(f"Statistics sent to {user_id}")
        except Exception as e:
            buttons=[
                [Button.inline("В меню", "/start")]
            ]   
            await self.client.send_message(user_id, message="Произошла ошибка, попробуйте снова!", buttons=buttons)
            logger.info(f"Fail to send statistic to {user_id}")


        


