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
from fastapi import UploadFile

from src.bot_logic.state_machine import get_state_machine
from src.bot_logic.utils import is_admin, media_to_upload_file, send_property_info
from src.bot_logic.database_service_client import get_database_service_client

load_dotenv()

LOG_FILE = os.path.join("logs", "add_property.log")

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename=LOG_FILE,
)
logger = logging.getLogger(__name__)

class AddPropertyHandler:
    def __init__(self, client: TelegramClient):
        self.client = client
        self.property_params = {}

    def register_handlers(self):
        self.client.add_event_handler(
            self.execute_param,
            events.NewMessage(),
        )
        self.client.add_event_handler(
            self.execute_param,
            events.CallbackQuery(),
        )
        self.client.add_event_handler(
            self.execute_images,
            events.NewMessage(pattern="(?i)upload_images"),
        )
        self.client.add_event_handler(
            self.execute_images,
            events.Album(),
        )
        self.client.add_event_handler(
            self.execute_start,
            events.NewMessage(pattern="/new_property"),
        )
        self.client.add_event_handler(
            self.execute_start,
            events.CallbackQuery(data="/new_property"),
        )

    async def execute_start(self, event):
        user_id = event.sender_id

        if not await is_admin(self.client, user_id):
            await self.client.send_message(user_id, "У вас нет прав на эту команду.")
            return

        logger.info(f"User {user_id} started property process")
        state_machine = get_state_machine()

        state_machine.starting_add_property(user_id)

        self.property_params["return_contact"] = str(user_id)

        state_machine.next_creating_property_pram(user_id)
        await state_machine.send_creating_property_message(self.client, user_id)

    def get_value_from_event(self, text: str, param_type):
        text = text.split(":")[-1]
        if param_type == "int":
            return int(text)
        elif param_type == "str":
            return text
        elif param_type == "bool":
            return bool(text.lower() == "true")
        else:
            raise ValueError(f"Unknown parameter type: {param_type}")

    async def execute_param(self, event):
        user_id = event.sender_id
        state_machine = get_state_machine()

        if state_machine.get_state(user_id) != "CREATING_PROPERTY":
            return
        
        if state_machine.get_creating_property_param(user_id) == "CONFIRMATION":
            return
        
        if state_machine.get_creating_property_param(user_id) == "IMAGES":
            message = "Полученое описание:\n"

            for key, value in self.property_params.items():
                if key != "return_contact":
                    message += f"{key}: {value}\n"
            message += "\nОтправьте фотографии, которые хотите загрузить. Чтобы завершить загрузку, отправьте сообщение 'Завершить загрузку'."
            await self.client.send_message(user_id, message)
            state_machine.next_creating_property_pram(user_id)
            return

        value = None
        text = None

        try:
            text = event.text.strip()
        except Exception:
            text = event.data.decode().strip()

        name, param_type = state_machine.get_cur_param_name_type(user_id)

        try:
            value = self.get_value_from_event(text, param_type)
        except ValueError as e:
            await self.client.send_message(user_id, f"Ошибка, неверный формат")
            await state_machine.send_creating_property_message(self.client, user_id)
            return
        
        if len(name.split(":")) > 1:
            name = name.split(":")[1]

        if type(value) == str and len(value.split(":")) > 1:
            value = value.split(":")[1]
            
        self.property_params[name] = value
        logger.info(f"User {user_id}: сохранен параметр {name} = {value}")

        state_machine.next_creating_property_pram(user_id)
        await state_machine.send_creating_property_message(self.client, user_id)

    async def handle_image(self, event: events.NewMessage.Event):
        logger.info(f"User {event.sender_id} started one image upload process")

        if event.media and (isinstance(event.media, MessageMediaPhoto) or isinstance(event.media, MessageMediaDocument)):
            try:
                upload_file = await media_to_upload_file(self.client, event.media)
                if upload_file:
                    upload_files = [upload_file]
                    return upload_files
                else:
                    await event.respond("Не удалось обработать изображение.")
                    return None

            except Exception as e:
                logger.error(f"Ошибка при обработке изображения: {e}")
                await event.respond("Произошла ошибка при обработке изображения.")
                return None

    async def handle_album(self, event: events.Album.Event):
        logger.info(f"User {event.sender_id} started album upload process")
        try:
            upload_files: List[bytes] = []
            for media in event.messages:
                if isinstance(media.media, MessageMediaPhoto):
                    upload_file = await media_to_upload_file(self.client, media.media)
                    
                    if upload_file:
                        upload_files.append(upload_file)
                    else:
                        logger.warning(f"Не удалось обработать одно из изображений в альбоме от user_id {event.sender_id}")
                logger.info(f"User {event.sender_id} обработал изображение в альбоме")
            if upload_files:
                return upload_files
            else:
                logger.warning(f"Не удалось обработать альбом от user_id {event.sender_id}")
                await event.respond("Не удалось обработать альбом.")
                return None

        except Exception as e:
            logger.error(f"Ошибка при обработке альбома: {e}")
            await event.respond("Произошла ошибка при обработке альбома.")

    async def execute_images(self, event):
        user_id = event.sender_id
        state_machine = get_state_machine()

        logger.info(f"User {user_id} started image upload process")

        if state_machine.get_creating_property_param(user_id) != "CONFIRMATION":
            return
        
        images: List[bytes] = []

        buttons = [Button.inline("В меню", "/start")]

        try:
            if isinstance(event, events.Album.Event):
                images = await self.handle_album(event)
            else:
                if event.photo:
                    images = await self.handle_image(event)
                else:
                    await event.respond("Не удалось обработать изображение.", buttons=buttons)
                    return

        except Exception as e:
            logger.error(f"Ошибка при получении фотографий из чата {event.chat_id}: {e}")
            images = None
            return
        
        if not images:
            await self.client.send_message(user_id, "Не удалось обработать изображения.", buttons=buttons)
            return
        
        logger.info(f"images saved")
        
        try:
            logger.info(f"property_params: {self.property_params}")
            database_client = get_database_service_client()
            respond = await database_client.new_property(user_id, self.property_params)
            property_id = respond["property_id"]

            for user in respond["users_id"]:
                message = "Посмотрите на новое объявление, подъодящее под ваши фильтры!"
                buttons = [ 
                    [Button.inline("Связаться с риелтором 🤝", f"like:-:{property_id}")],
                    [Button.inline("В избранное ❤️", f"to_favorites:{property_id}")],
                    [Button.inline("В меню", "/start")]
                ]
                await send_property_info(self.client, user, property_id, message=message, buttons=buttons)

            count = 0
            for image in images:
                logger.info(f"Uploading image for property {property_id}")
                await database_client.upload_image(property_id, count, image)
                count += 1

            await self.client.send_message(user_id, "Объект успешно загружен.", buttons=buttons)
            state_machine.end_creating_property(user_id)
        except Exception as e:
            logger.exception(f"Error sending images to database for user {user_id}: {e}")
            await self.client.send_message(user_id, "Произошла ошибка при загрузке фотографий", buttons=buttons)
            await state_machine.send_creating_property_message(self.client, user_id)

"""
    async def execute_images(self, event):
        user_id = event.sender_id
        state_machine = get_state_machine()

        logger.info(f"User {user_id} started image upload process")

        if state_machine.get_creating_property_param(user_id) != "CONFIRMATION":
            return
        
        images: List[bytes] = []

        try:
            if isinstance(event, events.Album.Event):
                images = await self.handle_album(event)
            else:
                if event.photo:
                    images = await self.handle_image(event)
                else:
                    await event.respond("Не удалось обработать изображение.")
                    return

        except Exception as e:
            logger.error(f"Ошибка при получении фотографий из чата {event.chat_id}: {e}")
            images = None
            return
        
        if not images:
            await self.client.send_message(user_id, "Не удалось обработать изображения.")
            return
        
        logger.info(f"images saved")
        
        try:
            logger.info(f"property_params: {self.property_params}")
            database_client = get_database_service_client()
            respond = await database_client.new_property(user_id, self.property_params)
            property_id = respond["property_id"]

            count = 0
            for image in images:
                logger.info(f"Uploading image for property {property_id}")
                await database_client.upload_image(property_id, count, image)
                count += 1

            await self.client.send_message(user_id, "Объект успешно загружен.")
            state_machine.end_creating_property(user_id)
        except Exception as e:
            logger.exception(f"Error sending images to database for user {user_id}: {e}")
            await self.client.send_message(user_id, "Произошла ошибка при загрузке фотографий")
            await state_machine.send_creating_property_message(self.client, user_id)

"""