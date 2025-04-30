from telethon import TelegramClient, events
import logging
import os

from src.bot_logic.state_machine import get_state_machine
from src.bot_logic.utils import go_to_neutral_state
from src.bot_logic.handlers.user_scenario_handlers.property_filters import NewPropertyFilterHandler
from src.bot_logic.handlers.user_scenario_handlers.update_handler import UpdateCommandHandler

LOG_FILE = os.path.join("logs", "bot.log")

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename=LOG_FILE,
)
logger = logging.getLogger(__name__)

class DefaultHandler:
    def __init__(self, client: TelegramClient):
        self.client = client
        self.property_filter_handler = NewPropertyFilterHandler(self.client)
        self.update_handler = UpdateCommandHandler(self.client)

    def register_handlers(self):
        self.client.add_event_handler(self.handle_default, events.NewMessage())

    async def handle_default(self, event):
        user_id = event.sender_id
        state_machine = get_state_machine()
        state = state_machine.get_property_state(user_id)
        update_param = state_machine.get_user_update_param(user_id)

        logger.info(f"User {user_id}: обработка события, state: {state}, update_param: {update_param}")

        if state == "NAME":
            event.text = "name:"+event.text
            await self.property_filter_handler.execute_param(event)
        elif state == "CITY":
            event.text = "city:"+event.text
            await self.property_filter_handler.execute_param(event)
        elif state == "AREAS":
            event.text = "areas:"+event.text
            await self.property_filter_handler.execute_param(event)
        elif state == "MIN_PRICE":
            event.text = "min_price:"+event.text
            await self.property_filter_handler.execute_param(event)
        elif state == "MAX_PRICE":
            event.text = "max_price:"+event.text
            await self.property_filter_handler.execute_param(event)
        elif state == "MIN_ROOMS":
            event.text = "min_rooms:"+event.text
            await self.property_filter_handler.execute_param(event)
        elif state == "MAX_ROOMS":
            event.text = "max_rooms:"+event.text
            await self.property_filter_handler.execute_param(event)
        elif state == "MIN_TOTAL_AREA":
            event.text = "min_total_area:"+event.text
            await self.property_filter_handler.execute_param(event)
        elif state == "MAX_TOTAL_AREA":
            event.text = "max_total_area:"+event.text
            await self.property_filter_handler.execute_param(event)
        elif state == "MIN_DEPOSIT":
            event.text = "min_deposit:"+event.text
            await self.property_filter_handler.execute_param(event)
        elif state == "MAX_DEPOSIT":
            event.text = "max_deposit:"+event.text
            await self.property_filter_handler.execute_param(event)
        elif state == "FLOOR":
            event.text = "floor:"+event.text
            await self.property_filter_handler.execute_param(event)
        elif state == "TOTAL_FLOORS":
            event.text = "total_floors:"+event.text
            await self.property_filter_handler.execute_total_floors(event)
        # ---------------------------------------------------
        elif update_param == "NAME":
            event.text = "upd_name:"+event.text
            await self.update_handler.execute_param_change(event)
        elif update_param == "CITY":
            event.text = "upd_city:"+event.text
            await self.update_handler.execute_param_change(event)
        elif update_param == "AREAS":
            event.text = "upd_areas:"+event.text
            await self.update_handler.execute_param_change(event)
        elif update_param == "MIN_PRICE":
            event.text = "upd_min_price:"+event.text
            await self.update_handler.execute_param_change(event)
        elif update_param == "MAX_PRICE":
            event.text = "upd_max_price:"+event.text
            await self.update_handler.execute_param_change(event)
        elif update_param == "MIN_ROOMS":
            event.text = "upd_min_rooms:"+event.text
            await self.update_handler.execute_param_change(event)
        elif update_param == "MAX_ROOMS":
            event.text = "upd_max_rooms:"+event.text
            await self.update_handler.execute_param_change(event)
        elif update_param == "MIN_TOTAL_AREA":
            event.text = "upd_min_total_area:"+event.text
            await self.update_handler.execute_param_change(event)
        elif update_param == "MAX_TOTAL_AREA":
            event.text = "upd_max_total_area:"+event.text
            await self.update_handler.execute_param_change(event)
        elif update_param == "MIN_DEPOSIT":
            event.text = "upd_min_deposit:"+event.text
            await self.update_handler.execute_param_change(event)
        elif update_param == "MAX_DEPOSIT":
            event.text = "upd_max_deposit:"+event.text
            await self.update_handler.execute_param_change(event)
        elif update_param == "FLOOR":
            event.text = "upd_floor:"+event.text
            await self.update_handler.execute_param_change(event)
        elif update_param == "TOTAL_FLOORS":
            event.text = "upd_total_floors:"+event.text
            await self.update_handler.execute_param_change(event)
        else:
            return
            await self.client.send_message(user_id, "Неизвестная команда")
            await go_to_neutral_state(user_id, client)

        