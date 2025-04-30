import logging
import re
import os

from telethon import TelegramClient, events, Button

from src.bot_logic.state_machine import get_state_machine
from src.bot_logic.utils import go_to_neutral_state, send_filter_info
from src.bot_logic.database_service_client import get_database_service_client
from src.bot_logic.messages import MESSAGES

LOG_FILE = os.path.join("logs", "update_handler.log")

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename=LOG_FILE,
)
logger = logging.getLogger(__name__)

class UpdateCommandHandler:
    def __init__(self, client: TelegramClient):
        self.client = client

    def register_handlers(self):
        self.client.add_event_handler(
            self.execute_start,
            events.NewMessage(pattern="/update_filter"),
        )
        self.client.add_event_handler(
            self.execute_start,
            events.CallbackQuery(data="/update_filter"),
        )
        self.client.add_event_handler(
            self.execute_choice_param,
            events.CallbackQuery(data=re.compile(r"^update:(.*)$")),
        )
        self.client.add_event_handler(
            self.execute_param_update,
            events.CallbackQuery(data=re.compile(r"^update_filter_choice:(.*)$")),
        )
        # ------------------
        self.client.add_event_handler(
            self.execute_param_change,
            events.NewMessage(pattern=re.compile(r"^upd_name:(.*)$")),
        )
        self.client.add_event_handler(
            self.execute_param_change,
            events.CallbackQuery(data=re.compile(r"^upd_property_type:(.*)$")),
        )
        self.client.add_event_handler(
            self.execute_param_change,
            events.CallbackQuery(data=re.compile(r"^upd_deal_type:(.*)$")),
        )
        self.client.add_event_handler(
            self.execute_param_change,
            events.NewMessage(pattern=re.compile(r"^upd_city:(.*)$")),
        )
        self.client.add_event_handler(
            self.execute_param_change,
            events.NewMessage(pattern=re.compile(r"^upd_areas:(.*)$")),
        )
        self.client.add_event_handler(
            self.execute_param_change,
            events.NewMessage(pattern=re.compile(r"^upd_min_price:(.*)$")),
        )
        self.client.add_event_handler(
            self.execute_param_change,
            events.NewMessage(pattern=re.compile(r"^upd_max_price:(.*)$")),
        )
        self.client.add_event_handler(
            self.execute_param_change,
            events.NewMessage(pattern=re.compile(r"^upd_min_rooms:(.*)$")),
        )
        self.client.add_event_handler(
            self.execute_param_change,
            events.NewMessage(pattern=re.compile(r"^upd_max_rooms:(.*)$")),
        )
        self.client.add_event_handler(
            self.execute_param_change,
            events.NewMessage(pattern=re.compile(r"^upd_min_total_area:(.*)$")),
        )
        self.client.add_event_handler(
            self.execute_param_change,
            events.NewMessage(pattern=re.compile(r"^upd_max_total_area:(.*)$")),
        )
        self.client.add_event_handler(
            self.execute_param_change,
            events.CallbackQuery(data=re.compile(r"^upd_balcony:(.*)$")),
        )
        self.client.add_event_handler(
            self.execute_param_change,
            events.CallbackQuery(data=re.compile(r"^upd_renovated:(.*)$")),
        )
        self.client.add_event_handler(
            self.execute_param_change,
            events.NewMessage(pattern=re.compile(r"^upd_min_deposit:(.*)$")),
        )
        self.client.add_event_handler(
            self.execute_param_change,
            events.NewMessage(pattern=re.compile(r"^upd_max_deposit:(.*)$")),
        )
        self.client.add_event_handler(
            self.execute_param_change,
            events.NewMessage(pattern=re.compile(r"^upd_floor:(.*)$")),
        )
        self.client.add_event_handler(
            self.execute_param_change,
            events.CallbackQuery(data=re.compile(r"^upd_is_active:(.*)$")),
        )
        self.client.add_event_handler(
            self.execute_param_change,
            events.NewMessage(pattern=re.compile(r"^upd_total_floors:(.*)$")),
        )

    async def execute_start(self, event):
        user_id = event.chat_id

        try:
            database_client = get_database_service_client()
            filter_list = await database_client.get_property_filters_list(user_id)

            message = "Выберите фильтр для изменения:"
            
            buttons = []

            for filter in filter_list:
                buttons.append([Button.inline(f"{filter['name']}", f"update:{filter['id']}")])
            
            buttons.append([Button.inline("В меню", "/start")])

            await self.client.send_message(event.chat_id, message, buttons=buttons)
        except Exception as e:
            await self.client.send_message(event.chat_id, "Произошла ошибка, попробуйте еще раз.")
            logger.exception(f"Update filters from database error: {e}")

    async def execute_choice_param(self, event):
        user_id = event.sender_id
        state_machine = get_state_machine()

        filter_id = event.data.decode().split(':')[1].strip()

        await send_filter_info(self.client, user_id, filter_id)

        message, buttons = MESSAGES["UPDATE_FILTER_CHOICE"]

        state_machine.start_update(user_id, filter_id)

        await self.client.send_message(event.chat_id, message, buttons=buttons)

    async def execute_param_update(self, event):
        user_id = event.sender_id
        state_machine = get_state_machine()

        message = "Выберете что хотите изменить"

        param_name = None

        param_name = event.data.decode().split(':')[1].strip()

        key = "UPDATE_FILTER:"+param_name
        message, buttons = MESSAGES[key]

        state_machine.set_update_param(user_id, param_name)
        await self.client.send_message(event.chat_id, message, buttons=buttons)

    async def execute_param_change(self, event):
        user_id = event.sender_id
        state_machine = get_state_machine()

        filter_id = state_machine.get_user_update_filter(user_id)

        buttons=[
            [Button.inline("Вернуться к изменению", f"update:{filter_id}")],
            [Button.inline("В меню", "/start")],
        ]

        value = None
        text = None

        try:
            text = event.text.split(":")[1].strip()
        except Exception:
            text = event.data.decode().split(':')[1].strip()

        if text == "-":
            value = None
        else:
            value = text

        param_name = state_machine.get_user_update_param(user_id)

        database_client = get_database_service_client()

        try:
            await database_client.update_property_filter(user_id, filter_id, param_name, value, type=state_machine.get_filter_param_type(param_name))
        except Exception as e:
            await event.respond("Ошибка обновления, попробуйте снова", buttons=buttons)
            state_machine.end_update(user_id)
            return
    
        state_machine.end_update(user_id)

        await self.client.send_message(user_id, "Изменение сохранено", buttons=buttons)
