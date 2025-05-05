import logging
import re
import os
from typing import Optional, List
from dotenv import load_dotenv
import json

from telethon import TelegramClient, events, Button

from src.bot_logic.state_machine import get_state_machine
from src.bot_logic.utils import go_to_neutral_state, send_current_state_message, format_filter_message
from src.bot_logic.database_service_client import get_database_service_client

load_dotenv()

LOG_FILE = os.path.join("logs", "property_filter.log")

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename=LOG_FILE,
)
logger = logging.getLogger(__name__)

class NewPropertyFilterHandler:
    def __init__(self, client: TelegramClient):
        self.client = client

    def register_handlers(self):
        self.client.add_event_handler(
            self.execute_start,
            events.NewMessage(pattern="/new_filter"),
        )
        self.client.add_event_handler(
            self.execute_start,
            events.CallbackQuery(data="/new_filter"),
        )
        self.client.add_event_handler(
            self.execute_param,
            events.NewMessage(pattern=re.compile(r"^name:(.*)$")),
        )
        self.client.add_event_handler(
            self.execute_param,
            events.CallbackQuery(data=re.compile(r"^property_type:(.*)$")),
        )
        self.client.add_event_handler(
            self.execute_param,
            events.CallbackQuery(data=re.compile(r"^deal_type:(.*)$")),
        )
        self.client.add_event_handler(
            self.execute_param,
            events.NewMessage(pattern=re.compile(r"^city:(.*)$")),
        )
        self.client.add_event_handler(
            self.execute_param,
            events.NewMessage(pattern=re.compile(r"^area:(.*)$")),
        )
        self.client.add_event_handler(
            self.execute_param,
            events.NewMessage(pattern=re.compile(r"^min_price:(.*)$")),
        )
        self.client.add_event_handler(
            self.execute_param,
            events.NewMessage(pattern=re.compile(r"^max_price:(.*)$")),
        )
        self.client.add_event_handler(
            self.execute_param,
            events.NewMessage(pattern=re.compile(r"^min_rooms:(.*)$")),
        )
        self.client.add_event_handler(
            self.execute_param,
            events.NewMessage(pattern=re.compile(r"^max_rooms:(.*)$")),
        )
        self.client.add_event_handler(
            self.execute_param,
            events.NewMessage(pattern=re.compile(r"^min_total_area:(.*)$")),
        )
        self.client.add_event_handler(
            self.execute_param,
            events.NewMessage(pattern=re.compile(r"^max_total_area:(.*)$")),
        )
        self.client.add_event_handler(
            self.execute_param,
            events.CallbackQuery(data=re.compile(r"^balcony:(.*)$")),
        )
        self.client.add_event_handler(
            self.execute_param,
            events.CallbackQuery(data=re.compile(r"^renovated:(.*)$")),
        )
        self.client.add_event_handler(
            self.execute_param,
            events.NewMessage(pattern=re.compile(r"^min_deposit:(.*)$")),
        )
        self.client.add_event_handler(
            self.execute_param,
            events.NewMessage(pattern=re.compile(r"^max_deposit:(.*)$")),
        )
        self.client.add_event_handler(
            self.execute_param,
            events.NewMessage(pattern=re.compile(r"^floor:(.*)$")),
        )
        self.client.add_event_handler(
            self.execute_param,
            events.CallbackQuery(data=re.compile(r"^is_active:(.*)$")),
        )
        self.client.add_event_handler(
            self.execute_total_floors,
            events.NewMessage(pattern=re.compile(r"^total_floors:(.*)$")),
        )
        self.client.add_event_handler(
            self.execute_confirmation,
            events.CallbackQuery(data=re.compile(r"^property_filter_confirmation:(.*)$")),
        )

    async def execute_start(self, event):
        user_id = event.sender_id
        logger.info(f"User {user_id} started new filter process")
        state_machine = get_state_machine()

        if not state_machine.is_valid_transition(user_id, "NEUTRAL"):
            await event.respond("Неправильный ввод, попробуйте снова")
            await send_current_state_message(user_id, self.client)
        state_machine.starting_property_filter(user_id)

        await send_current_state_message(user_id, self.client)

    async def execute_param(self, event):
        user_id = event.sender_id
        state_machine = get_state_machine()

        value = None
        text = None

        try:
            text = event.text.split(":")[1].strip()
        except Exception:
            text = event.data.decode().split(':')[1].strip()

        logger.info(f"on state text: {text}")
        if text == "-":
            value = None
        else:
            if state_machine.is_state_num(user_id):
                try:
                    value = int(text)
                except ValueError:
                    await event.respond("Неправильный ввод, требуется число, попробуйте снова")
                    await send_current_state_message(user_id, self.client)
                    return
                logger.info(f"int value: {value}")
            elif state_machine.is_state_bool(user_id):
                value = bool(text.lower() == "true")
                logger.info(f"bool value: {value}")
            elif state_machine.is_state_list(user_id):
                value = text
                logger.info(f"list value: {value}")
            else:
                value = str(text)
                logger.info(f"str value: {value}")

        state = state_machine.get_property_state(user_id)
        state_machine.save_filter_info(user_id, state, value)
        state_machine.next_property_filter(user_id)

        await send_current_state_message(user_id, self.client)

    async def execute_total_floors(self, event):
        user_id = event.sender_id
        state_machine = get_state_machine()

        if not state_machine.is_valid_transition(user_id, "TOTAL_FLOORS"):
            await event.respond("Неправильный ввод, попробуйте снова")
            await send_current_state_message(user_id, self.client)
            return

        total_floors = 0
        if event.text.split(":")[1].strip() == "-":
            total_floors = None
        else:
            try:
                total_floors = int(event.text.split(":")[1].strip())
            except ValueError:
                await event.respond("Неправильный ввод, попробуйте снова")
                await send_current_state_message(user_id, self.client)
                return

        state_machine.save_filter_info(user_id, "TOTAL_FLOORS", total_floors)
        state_machine.next_property_filter(user_id)

        property_filter = state_machine.get_property_filter(user_id)
        if property_filter:
            filter_string = format_filter_message(property_filter)
        else:
            filter_string = "Не удалось получить информацию о фильтре"

        await event.respond(f"Получившийся фильтр:\n{filter_string}")

        await send_current_state_message(user_id, self.client)

    async def execute_confirmation(self, event):
        user_id = event.sender_id
        state_machine = get_state_machine()

        if not state_machine.is_valid_transition(user_id, "CONFIRMATION"):
            await event.respond("Неправильный ввод, попробуйте снова")
            await send_current_state_message(user_id, self.client)
            return

        confirmation = event.data.decode().split(':')[1].strip()

        if confirmation == "yes":
            database_client = get_database_service_client(os.getenv("DATABASE_SERVICE_URL", "http://db_service:8005"))
            await database_client.new_property_filter(user_id=user_id, filter=state_machine.get_property_filter(user_id))
            await event.respond("Фильтр успешно создан")
        else:
            await event.respond("Создание фильтра отменено")

        await go_to_neutral_state(user_id, self.client)

"""
    async def execute_name(self, event):
        user_id = event.sender_id
        state_machine = get_state_machine()

        if not state_machine.is_valid_transition(user_id, "NAME"):
            await event.respond("Неправильный ввод, попробуйте снова")
            await send_current_state_message(user_id, self.client)
            return

        state_machine.save_filter_info(user_id, "NAME", event.text.split(':')[1].strip())
        state_machine.next_property_filter(user_id)

        await send_current_state_message(user_id, self.client)

    async def execute_property_type(self, event):
        user_id = event.sender_id
        state_machine = get_state_machine()

        if not state_machine.is_valid_transition(user_id, "PROPERTY_TYPE"):
            await event.respond("Неправильный ввод, попробуйте снова")
            await send_current_state_message(user_id, self.client)
            return

        property_type = event.data.decode().split(':')[1].strip()

        if property_type == "-":
            property_type = None

        state_machine.save_filter_info(user_id, "PROPERTY_TYPE", property_type)
        state_machine.next_property_filter(user_id)

        await send_current_state_message(user_id, self.client)

    async def execute_deal_type(self, event):
        user_id = event.sender_id
        state_machine = get_state_machine()

        if not state_machine.is_valid_transition(user_id, "DEAL_TYPE"):
            await event.respond("Неправильный ввод, попробуйте снова")
            await send_current_state_message(user_id, self.client)
            return

        deal_type = event.data.decode().split(':')[1].strip()

        if deal_type == "-":
            deal_type = None

        state_machine.save_filter_info(user_id, "DEAL_TYPE", deal_type)
        state_machine.next_property_filter(user_id)

        await send_current_state_message(user_id, self.client)

    async def execute_city(self, event):
        user_id = event.sender_id
        state_machine = get_state_machine()

        if not state_machine.is_valid_transition(user_id, "CITY"):
            await event.respond("Неправильный ввод, попробуйте снова")
            await send_current_state_message(user_id, self.client)
            return

        city = event.text.split(':')[1].strip()

        if city == "-":
            city = None

        state_machine.save_filter_info(user_id, "CITY", city)
        state_machine.next_property_filter(user_id)

        await send_current_state_message(user_id, self.client)

    async def execute_areas(self, event):
        user_id = event.sender_id
        state_machine = get_state_machine()

        if not state_machine.is_valid_transition(user_id, "AREAS"):
            await event.respond("Неправильный ввод, попробуйте снова")
            await send_current_state_message(user_id, self.client)
            return

        areas_string = event.text.split(":")[1].strip()
        areas_list = [area.strip() for area in areas_string.split(",")]

        areas_string_for_db = " ".join(areas_list)
        areas_string_for_db = areas_string_for_db.strip()

        if areas_string_for_db == "-":
            areas_string_for_db = None

        state_machine.save_filter_info(user_id, "AREAS", areas_string_for_db)
        state_machine.next_property_filter(user_id)

        await send_current_state_message(user_id, self.client)

    async def execute_min_price(self, event):
        user_id = event.sender_id
        state_machine = get_state_machine()

        if not state_machine.is_valid_transition(user_id, "MIN_PRICE"):
            await event.respond("Неправильный ввод, попробуйте снова")
            await send_current_state_message(user_id, self.client)
            return

        min_price = 0
        try:
            min_price = int(event.text.split(":")[1].strip())
        except ValueError:
            await event.respond("Неправильный ввод, попробуйте снова")
            await send_current_state_message(user_id, self.client)
            return

        state_machine.save_filter_info(user_id, "MIN_PRICE", min_price)
        state_machine.next_property_filter(user_id)

        await send_current_state_message(user_id, self.client)

    async def execute_max_price(self, event):
        user_id = event.sender_id
        state_machine = get_state_machine()

        if not state_machine.is_valid_transition(user_id, "MAX_PRICE"):
            await event.respond("Неправильный ввод, попробуйте снова")
            await send_current_state_message(user_id, self.client)
            return

        max_price = 0
        try:
            max_price = int(event.text.split(":")[1].strip())
        except ValueError:
            await event.respond("Неправильный ввод, попробуйте снова")
            await send_current_state_message(user_id, self.client)
            return

        state_machine.save_filter_info(user_id, "MAX_PRICE", max_price)
        state_machine.next_property_filter(user_id)

        await send_current_state_message(user_id, self.client)

    async def execute_min_rooms(self, event):
        user_id = event.sender_id
        state_machine = get_state_machine()

        if not state_machine.is_valid_transition(user_id, "MIN_ROOMS"):
            await event.respond("Неправильный ввод, попробуйте снова")
            await send_current_state_message(user_id, self.client)
            return

        min_rooms = 0
        if event.text.split(":")[1].strip() == "-":
            min_rooms = None
        else:
            try:
                min_rooms = int(event.text.split(":")[1].strip())
            except ValueError:
                await event.respond("Неправильный ввод, попробуйте снова")
                await send_current_state_message(user_id, self.client)
                return

        state_machine.save_filter_info(user_id, "MIN_ROOMS", min_rooms)
        state_machine.next_property_filter(user_id)

        await send_current_state_message(user_id, self.client)

    async def execute_max_rooms(self, event):
        user_id = event.sender_id
        state_machine = get_state_machine()

        if not state_machine.is_valid_transition(user_id, "MAX_ROOMS"):
            await event.respond("Неправильный ввод, попробуйте снова")
            await send_current_state_message(user_id, self.client)
            return

        max_rooms = 0
        if event.text.split(":")[1].strip() == "-":
            max_rooms = None
        else:
            try:
                max_rooms = int(event.text.split(":")[1].strip())
            except ValueError:
                await event.respond("Неправильный ввод, попробуйте снова")
                await send_current_state_message(user_id, self.client)
                return

        state_machine.save_filter_info(user_id, "MAX_ROOMS", max_rooms)
        state_machine.next_property_filter(user_id)

        await send_current_state_message(user_id, self.client)

    async def execute_min_total_area(self, event):
        user_id = event.sender_id
        state_machine = get_state_machine()

        if not state_machine.is_valid_transition(user_id, "MIN_TOTAL_AREA"):
            await event.respond("Неправильный ввод, попробуйте снова")
            await send_current_state_message(user_id, self.client)
            return

        min_total_area = 0
        if event.text.split(":")[1].strip() == "-":
            min_total_area = None
        else:
            try:
                min_total_area = int(event.text.split(":")[1].strip())
            except ValueError:
                await event.respond("Неправильный ввод, попробуйте снова")
                await send_current_state_message(user_id, self.client)
                return

        state_machine.save_filter_info(user_id, "MIN_TOTAL_AREA", min_total_area)
        state_machine.next_property_filter(user_id)

        await send_current_state_message(user_id, self.client)

    async def execute_max_total_area(self, event):
        user_id = event.sender_id
        state_machine = get_state_machine()

        if not state_machine.is_valid_transition(user_id, "MAX_TOTAL_AREA"):
            await event.respond("Неправильный ввод, попробуйте снова")
            await send_current_state_message(user_id, self.client)
            return

        max_total_area = 0
        if event.text.split(":")[1].strip() == "-":
            max_total_area = None
        else:
            try:
                max_total_area = int(event.text.split(":")[1].strip())
            except ValueError:
                await event.respond("Неправильный ввод, попробуйте снова")
                await send_current_state_message(user_id, self.client)
                return

        state_machine.save_filter_info(user_id, "MAX_TOTAL_AREA", max_total_area)
        state_machine.next_property_filter(user_id)

        await send_current_state_message(user_id, self.client)

    async def execute_balcony(self, event):
        user_id = event.sender_id
        state_machine = get_state_machine()

        if not state_machine.is_valid_transition(user_id, "BALCONY"):
            await event.respond("Неправильный ввод, попробуйте снова")
            await send_current_state_message(user_id, self.client)
            return

        balcony = event.data.decode().split(":")[1].strip()

        if balcony == "-":
            balcony = None
        elif balcony == "yes":
            balcony = True
        elif balcony == "no":
            balcony = False
        else:
            await event.respond("Неправильный ввод, попробуйте снова")
            await send_current_state_message(user_id, self.client)
            return

        state_machine.save_filter_info(user_id, "BALCONY", balcony)
        state_machine.next_property_filter(user_id)

        await send_current_state_message(user_id, self.client)

    async def execute_renovated(self, event):
        user_id = event.sender_id
        state_machine = get_state_machine()

        if not state_machine.is_valid_transition(user_id, "RENOVATED"):
            await event.respond("Неправильный ввод, попробуйте снова")
            await send_current_state_message(user_id, self.client)
            return

        renovated = event.data.decode().split(":")[1].strip()

        if renovated == "-":
            renovated = None
        elif renovated == "yes":
            renovated = True
        elif renovated == "no":
            renovated = False
        else:
            await event.respond("Неправильный ввод, попробуйте снова")
            await send_current_state_message(user_id, self.client)
            return

        state_machine.save_filter_info(user_id, "RENOVATED", renovated)
        state_machine.next_property_filter(user_id)

        await send_current_state_message(user_id, self.client)

    async def execute_min_deposit(self, event):
        user_id = event.sender_id
        state_machine = get_state_machine()

        if not state_machine.is_valid_transition(user_id, "MIN_DEPOSIT"):
            await event.respond("Неправильный ввод, попробуйте снова")
            await send_current_state_message(user_id, self.client)
            return

        deposit = 0
        if event.text.split(":")[1].strip() == "-":
            deposit = None
        else:
            try:
                deposit = int(event.text.split(":")[1].strip())
            except ValueError:
                await event.respond("Неправильный ввод, попробуйте снова")
                await send_current_state_message(user_id, self.client)
                return

        state_machine.save_filter_info(user_id, "MIN_DEPOSIT", deposit)
        state_machine.next_property_filter(user_id)

        await send_current_state_message(user_id, self.client)

    async def execute_max_deposit(self, event):
        user_id = event.sender_id
        state_machine = get_state_machine()

        if not state_machine.is_valid_transition(user_id, "MAX_DEPOSIT"):
            await event.respond("Неправильный ввод, попробуйте снова")
            await send_current_state_message(user_id, self.client)
            return

        deposit = 0
        if event.text.split(":")[1].strip() == "-":
            deposit = None
        else:
            try:
                deposit = int(event.text.split(":")[1].strip())
            except ValueError:
                await event.respond("Неправильный ввод, попробуйте снова")
                await send_current_state_message(user_id, self.client)
                return

        state_machine.save_filter_info(user_id, "MAX_DEPOSIT", deposit)
        state_machine.next_property_filter(user_id)

        await send_current_state_message(user_id, self.client)

    async def execute_floor(self, event):
        user_id = event.sender_id
        state_machine = get_state_machine()

        if not state_machine.is_valid_transition(user_id, "FLOOR"):
            await event.respond("Неправильный ввод, попробуйте снова")
            await send_current_state_message(user_id, self.client)
            return

        floor = 0
        if event.text.split(":")[1].strip() == "-":
            floor = None
        else:
            try:
                floor = int(event.text.split(":")[1].strip())
            except ValueError:
                await event.respond("Неправильный ввод, попробуйте снова")
                await send_current_state_message(user_id, self.client)
                return

        state_machine.save_filter_info(user_id, "FLOOR", floor)
        state_machine.next_property_filter(user_id)

        await send_current_state_message(user_id, self.client)
"""