import io
import os
import logging

from telethon import TelegramClient, events, Button
from telethon.types import User
from telethon.types import MessageMediaPhoto
from telethon.types import InputMediaPhoto
from fastapi import UploadFile
from typing import List
import base64

from src.bot_logic.database_service_client import get_database_service_client
from src.bot_logic.state_machine import get_state_machine
from src.bot_logic.messages import MESSAGES

LOG_FILE = os.path.join("logs", "bot.log")

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename=LOG_FILE,
)
logger = logging.getLogger(__name__)

async def is_admin(client: TelegramClient, user_id: int) -> bool:
    try:
        database_service = get_database_service_client()

        return await database_service.is_admin(user_id)
    except Exception as e:
        logger.error(f"Error checking admin status: {e}")
        return False

async def go_to_neutral_state(user_id, client: TelegramClient):
    state_machine = get_state_machine()
    state_machine.go_neutral(user_id)

    buttons = []

    is_user_admin = await is_admin(client, user_id)
    logger.info(f"User {user_id} is admin: {is_user_admin}")

    if is_user_admin:
        buttons.append([Button.inline("Добавить объявление", "/new_property")])
        buttons.append([Button.inline("Просмотр объявлений", "show_properties:0")])
        buttons.append([Button.inline("Статистика", "/get_statistics")])
        buttons.append([Button.inline("Перестать быть админом", "/unregister_admin")])
    else:
        buttons = [
            [Button.inline("Новый фильтр ❇️", "/new_filter")],
            [Button.inline("Инструкция 🧾", "/help")],
            [Button.inline("Избранное ⭐️", "/favorites_list:0")],
            [Button.inline("Мои фильтры 🈴", "/filters_list")],
            [Button.inline("Изменить фильтр 🆙", "/update_filter")],
            [Button.inline("Удалить фильтр ❌", "/delete_filter")],
            [Button.inline("Смотреть объявления 👀", "/search")],
            # это стартовое меню, будет допольняться по мере разработки
        ]

    await client.send_message(user_id, "Выберите Инструкция чтобы узнать о моих функциях!", buttons=buttons)
    return

async def send_current_state_message(user_id, client: TelegramClient):
    state_machine = get_state_machine()
    command_state = state_machine.get_state(user_id)
    state = "NEUTRAL"

    if command_state == "PROPERTY_FILTERS":
        state = state_machine.get_property_state(user_id)

    state_key = command_state+":"+state

    if state_key in MESSAGES:
        message, buttons = MESSAGES[state_key]
        await client.send_message(user_id, message, buttons=buttons)
    else:
        await client.send_message(user_id, "К сожалению произошла ошибка ввода, перенаправляю в меню...")
        await go_to_neutral_state(user_id, client)

    return

async def get_user_link(client: TelegramClient, user_id: int) -> str:
    try:
        entity = await client.get_entity(user_id)
        if isinstance(entity, User) and entity.username:
            return f"t.me/{entity.username}"
        else:
            return f"ID: {user_id}"
    except Exception as e:
        return f"ID: {user_id}"
    
def format_filter_message(filter_info):
    message = f"Фильтр: {filter_info.get('name', 'Не указано')}\n"

    if 'property_type' in filter_info and filter_info['property_type']:
        message += f"Тип: {filter_info['property_type']}\n"
    else:
        message += "Тип: Не указано\n"

    if 'city' in filter_info and filter_info['city']:
        message += f"Город: {filter_info['city']}\n"
    else:
        message += "Город: Не указано\n"

    if 'areas' in filter_info and filter_info['areas']:
        message += f"Районы: {filter_info['areas']}\n"
    else:
        message += "Районы: Не указано\n"

    def format_range(min_value, max_value, label):
        if min_value is not None and max_value is not None:
            return f"{label}: {min_value}-{max_value}\n"
        elif min_value is not None:
            return f"{label}: от {min_value}\n"
        elif max_value is not None:
            return f"{label}: до {max_value}\n"
        else:
            return f"{label}: Не указано\n"

    message += format_range(filter_info.get('min_price'), filter_info.get('max_price'), "Цена")
    message += format_range(filter_info.get('min_total_area'), filter_info.get('max_total_area'), "Площадь")
    message += format_range(filter_info.get('min_rooms'), filter_info.get('max_rooms'), "Кол-во комнат")
    message += format_range(filter_info.get('min_deposit'), filter_info.get('max_deposit'), "Депозит")

    message += f"Балкон: {'Да' if filter_info.get('balcony', False) else 'Нет'}\n"

    renovated = filter_info.get('renovated')
    if renovated == 'yes':
        message += "Ремонт: С ремонтом\n"
    elif renovated == 'no':
        message += "Ремонт: Требуется ремонт\n"
    else:
        message += "Ремонт: Не указано\n"

    floor = filter_info.get('floor')
    if floor is not None:
        message += f"Этаж: {floor}\n"
    else:
        message += "Этаж: Не указано\n"

    total_floors = filter_info.get('total_floors')
    if total_floors is not None:
        message += f"Всего этажей: {total_floors}\n"
    else:
        message += "Всего этажей: Не указано\n"

    message += f"Активен: {'Да' if filter_info.get('is_active', False) else 'Нет'}\n"

    return message

async def send_filter_info(client, user_id: int, filter_id: int):
    database_service = get_database_service_client()
    try:
        filter_info = await database_service.get_property_filter(filter_id)
        if not filter_info:
            await client.send_message(user_id, "Фильтр не найден.")
            return

        logger.info(f"Filter info: {filter_info}")
        message = format_filter_message(filter_info)

        await client.send_message(user_id, message)
    except Exception as e:
        await client.send_message(user_id, "Произошла ошибка при получении информации о фильтре.")
        logger.error(f"Error getting filter info: {e}")

async def media_to_upload_file(client: TelegramClient, media: MessageMediaPhoto) -> UploadFile | None:
    logger.info(f"Загрузка медиафайла: {media}")
    try:
        photo_bytes = await client.download_media(media, bytes)
        logger.info(f"Got here 1 type:{type(photo_bytes)}")

        if photo_bytes is None:
            logger.error("Не удалось загрузить медиафайл.")
            return None
        
        return photo_bytes

    except Exception as e:
        logger.error(f"Ошибка при загрузке медиафайла: {e}")
        return None

async def send_property_info(client: TelegramClient, user_id: int, property_id: int, message="", is_admin=False, buttons=None):
    datatbase_service = get_database_service_client()

    try:
        property_info = await datatbase_service.get_property_description(property_id)
        if not property_info:
            await client.send_message(user_id, "Объявление не найдено.")
            go_to_neutral_state(user_id, client)
            return

        logger.info(f"Property info: {property_info}")
        
        message += "\n"
        message += f"Объявление {property_info.get('id', 'Не указано')}\n\n"

        message += f"Состояние: {property_info.get('state', 'Не указано')}\n"
        message += f"Адрес: {property_info.get('city', 'Не указано')}"
        message += "{property_info.get('area', 'Не указано')}"
        message += "{property_info.get('street', 'Не указано')}"
        message += "{property_info.get('house_number', 'Не указано')}"
        message += "{property_info.get('apartment_number', 'Не указано')}\n"
        
        message += f"Тип: {property_info.get('property_type', 'Не указано')}\n"
        message += f"Тип сделки: {property_info.get('deal_type', 'Не указано')}\n"
        message += f"Цена: {property_info.get('price', 'Не указано')}\n\n"
        message += f"Депозит: {property_info.get('deposit', 'Не указано')}\n"

        message += f"Описание: {property_info.get('description', 'Не указано')}\n\n"

        message += "Параметры:\n"

        message += f"Комнат: {property_info.get('rooms', 'Не указано')}\n"
        message += f"Площадь: {property_info.get('total_area', 'Не указано')}\n"
        message += f"Этаж: {property_info.get('floor', 'Не указано')}\n"
        message += f"Всего этажей: {property_info.get('total_floors', 'Не указано')}\n"

        message += f"Балкон: {'Да' if property_info.get('balcony', False) else 'Нет'}\n"
        message += f"Ремонт: {property_info.get('renovated', 'Не указано')}\n"

        photos_bytes = await datatbase_service.get_property_photos(property_id)

        if not photos_bytes:
            await client.send_message(user_id, "Нет фотографий для этого объявления.")
            return
        
        photos = []

        for photo_bytes in photos_bytes:
            photo = await client.upload_file(
                file=photo_bytes,
                file_name="photo.jpg",
            )
            photos.append(photo)
        
        logger.info(f"Got {len(photos)} photos for property {property_id}")

        if await datatbase_service.is_admin(user_id) and buttons == None:
            buttons = [
                    [Button.inline("Получить статистику", f"get_property_statistics:{property_id}"), 
                    Button.inline("Снова активно", f"property_back_active:{property_id}")],
                    [Button.inline("В аренде", f"become_rented_property:{property_id}"),
                    Button.inline("Продано", f"sold_property:{property_id}")],
                    [Button.inline("Удалить", f"delete_property:{property_id}"),
                    Button.inline("В меню", "/start")]
                ]

        await client.send_file(user_id, photos)

        await client.send_message(user_id, message, buttons=buttons)
        logger.info(f"Message with photos sent to {user_id}")

    except Exception as e:
        logger.error(f"Error getting property info: {e}")
        await client.send_message(user_id, "Произошла ошибка при получении информации о фильтре.")
        return


