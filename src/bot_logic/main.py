import asyncio
import logging

from telethon import TelegramClient, events
from fastapi import Request
import uvicorn
from dotenv import load_dotenv
import os
import requests

from src.settings import TGBotSettings

from src.bot_logic.handlers.user_scenario_handlers.property_filters import NewPropertyFilterHandler
from src.bot_logic.handlers.user_scenario_handlers.help_handler import HelpCommandHandler
from src.bot_logic.handlers.user_scenario_handlers.search_handler import SearchCommandHandler
from src.bot_logic.handlers.user_scenario_handlers.list_handler import ListCommandHandler
from src.bot_logic.handlers.user_scenario_handlers.delete_handler import DeleteCommandHandler
from src.bot_logic.handlers.user_scenario_handlers.update_handler import UpdateCommandHandler

from src.bot_logic.handlers.user_scenario_handlers.favorites_list import FavoritesListHandler
from src.bot_logic.handlers.user_scenario_handlers.remove_from_favorites import DeleteFromFavoritesCommandHandler
from src.bot_logic.handlers.user_scenario_handlers.to_favorites import ToFavoritesCommandHandler

from src.bot_logic.handlers.default_handler import DefaultHandler
from src.bot_logic.handlers.start_handler import StartCommandHandler

from src.bot_logic.handlers.admin_scenario_handlers.register_admin_handler import RegisterAdminCommandHandler
from src.bot_logic.handlers.admin_scenario_handlers.add_property_handler import AddPropertyHandler
from src.bot_logic.handlers.admin_scenario_handlers.add_property_file import AddPropertyFileHandler
from src.bot_logic.handlers.admin_scenario_handlers.ad_description_handler import AdDescriptionCommandHandler
from src.bot_logic.handlers.admin_scenario_handlers.show_properties import ShowPropertiesHandler

from src.bot_logic.handlers.admin_scenario_handlers.unregister_admin_handler import UnregisterAdminCommandHandler
from src.bot_logic.handlers.admin_scenario_handlers.delete_property_handler import DeletePropertyHandler
from src.bot_logic.handlers.admin_scenario_handlers.sold_rented_free_property_handler import SoldRentedFreePropertyHandler
from src.bot_logic.handlers.admin_scenario_handlers.get_property_statistics_handler import GetPropertyStatisticsHandler
from src.bot_logic.handlers.admin_scenario_handlers.get_statistics_handler import GetStatisticsHandler



# Импорт handler
# from src.bot_logic.handlers.<handler определенной команды> import <класс Handler>

load_dotenv()

LOG_FILE = os.path.join("logs", "bot.log")

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename=LOG_FILE,
)
logger = logging.getLogger(__name__)

settings = TGBotSettings()

client = TelegramClient("bot_session", settings.api_id, settings.api_hash).start(
    bot_token=settings.token,
)

async def register_handlers(client: TelegramClient):
    new_property_filter_handler = NewPropertyFilterHandler(client)
    new_property_filter_handler.register_handlers()

    start_handler = StartCommandHandler(client)
    start_handler.register_handlers()

    help_handler = HelpCommandHandler(client)
    help_handler.register_handlers()

    list_handler = ListCommandHandler(client)
    list_handler.register_handlers()

    search_handler = SearchCommandHandler(client)
    search_handler.register_handlers()

    delete_handler = DeleteCommandHandler(client)
    delete_handler.register_handlers()

    ad_description_handler = AdDescriptionCommandHandler(client)
    ad_description_handler.register_handlers()

    register_admin_handler = RegisterAdminCommandHandler(client)
    register_admin_handler.register_handlers()

    add_property_handler = AddPropertyHandler(client)
    add_property_handler.register_handlers()

    add_property_file_handler = AddPropertyFileHandler(client)
    add_property_file_handler.register_handlers()

    update_handler = UpdateCommandHandler(client)
    update_handler.register_handlers()

    show_properties_handler = ShowPropertiesHandler(client)
    show_properties_handler.register_handlers()

    unregister_admin_handler = UnregisterAdminCommandHandler(client)
    unregister_admin_handler.register_handlers()

    delete_property_handler = DeletePropertyHandler(client)
    delete_property_handler.register_handlers()

    change_property_status_handler = SoldRentedFreePropertyHandler(client)
    change_property_status_handler.register_handlers()

    get_property_statistics = GetPropertyStatisticsHandler(client)
    get_property_statistics.register_handlers()

    get_statistics = GetStatisticsHandler(client)
    get_statistics.register_handlers()

    favorites_list = FavoritesListHandler(client)
    favorites_list.register_handlers()

    delete_from_favorites = DeleteFromFavoritesCommandHandler(client)
    delete_from_favorites.register_handlers()

    to_favorites = ToFavoritesCommandHandler(client)
    to_favorites.register_handlers()

    default_handler = DefaultHandler(client)
    default_handler.register_handlers()

async def main() -> None:
    await register_handlers(client)
    while True:
        try:
            await asyncio.sleep(60)
        except Exception as e:
            logger.exception(f"Error in main loop: {e}")
            await asyncio.sleep(60)

logger.info("Run the event loop to start receiving messages")

try:
    client.start(bot_token=settings.token)
    with client:
        try:
            client.loop.run_until_complete(main())
        except KeyboardInterrupt:
            pass
        except Exception as exc:
            logger.exception(
                "Main loop raised error.",
                extra={"exc": exc},
            )
finally:
    client.disconnect()
    logger.info("Bot stopped")