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
import xmltodict
import pandas as pd
from urllib.parse import urlencode
import aiohttp
import requests

from src.bot_logic.state_machine import get_state_machine
from src.bot_logic.utils import is_admin, go_to_neutral_state, send_property_info
from src.bot_logic.database_service_client import get_database_service_client

load_dotenv()

LOG_FILE = os.path.join("logs", "add_property.log")

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename=LOG_FILE,
)
logger = logging.getLogger(__name__)

def get_property_type(pr_type: str):
    if pr_type == "Квартиры":
        return "квартира"
    if pr_type == "Дома, дачи, коттеджи":
        return "дом"
    if pr_type == "Комнаты":
        return "комната"
    if pr_type == "Земельные участки":
        return "участок"
    if pr_type == "Коммерческая недвижимость":
        return "коммерческая"
    raise ValueError("Не задан параметр Category")

def get_rooms(rooms: str):
    if rooms == "Студия":
        return 1
    if rooms == "10 и более":
        return 10
    if rooms == "Своб. планировка":
        return 0
    try:
        return int(rooms)
    except:
        raise ValueError("Неправильно задано кол-во комнат: допускается 1-9, Студия, 10 и более, Своб. планировка")

async def get_image(image_url: str) -> bytes:
    async with aiohttp.ClientSession() as session:
        image_url = image_url.strip()
        url_type = image_url.removeprefix("https://").removeprefix("http://")
        logger.info(f"url_type: {url_type}, image_url: {image_url}")

        if url_type.startswith("disk.yandex.ru"):
            public_key = image_url.rsplit('/', 1)[-1]
            base_url = 'https://cloud-api.yandex.net/v1/disk/public/resources/download?'
            public_key = image_url

            final_url = base_url + urlencode(dict(public_key=public_key))
            response = requests.get(final_url)
            download_url = response.json()['href']

            async with session.get(download_url) as file_resp:
                if file_resp.status != 200:
                    raise Exception(f"Failed to download image: {file_resp.status}")
                return await file_resp.read()

        else:
            async with session.get(image_url) as resp:
                if resp.status != 200:
                    raise Exception(f"Failed to download image: {resp.status}")
                return await resp.read()

class AddPropertyFileHandler:
    def __init__(self, client: TelegramClient):
        self.client = client
        self.property_params = {}

    def register_handlers(self):
        self.client.add_event_handler(
            self.execute_load,
            events.NewMessage(),
        )
        self.client.add_event_handler(
            self.execute_start,
            events.NewMessage(pattern="/new_property_file"),
        )
        self.client.add_event_handler(
            self.execute_start,
            events.CallbackQuery(data="/new_property_file"),
        )

    async def execute_start(self, event):
        user_id = event.sender_id

        if not await is_admin(self.client, user_id):
            await self.client.send_message(user_id, "У вас нет прав на эту команду.")
            return

        logger.info(f"User {user_id} started property process")

        state_machine = get_state_machine()
        state_machine.starting_load_by_file_property(user_id)

        message = "Пришлите файл с описанием недвижимости в таком формате:\n"
        message+="Шаблон: https://www.avito.ru/autoload/documentation/templates/67068\n"

        message += "Обязательные поля: Category, OperationType, Price, Description, \
            ImageUrls (хотя бы одно сообщение, в объявление попадут первые 10)\n"
        message += "Поля, рекомендованные к заполнению: Id, BalconyOrLoggiaMulti, MarketType, Square, Floor, Floors, DepositAmount\n"


        await self.client.send_message(user_id, message)

    async def execute_load(self, event):
        user_id = event.chat_id
        state_machine = get_state_machine()

        logger.info("Запущен процесс загрузки для {user_id}")

        if state_machine.get_state(user_id) != "LOADING_FILE":
            return
        
        if not event.file or not event.file.name.endswith('.xlsx'):
            await self.client.send_message(user_id, "Файл отстутствует или не соответствует формату: пришлите .xlsx файл, соответствующий шаблону: https://www.avito.ru/autoload/documentation/templates")

        file_path = await event.download_media()

        xls = pd.ExcelFile(file_path)
        sheet_name = xls.sheet_names[1]

        df = pd.read_excel(
            xls,
            sheet_name=sheet_name,
            header=1,
            skiprows=[2, 3]
        )

        df.dropna(how='all', inplace=True)
        
        message = ""

        for _, row in df.iterrows():
            logger.info(f"Processing_property: {row}")
            property_id = 0
            try:
                payload = {}
                payload["return_contact"] = str(user_id)
                pr_type = row.get("Category", "Квартиры")
                payload["property_type"] = get_property_type(pr_type)
                op_type = row.get("OperationType", "Продам")
                payload["deal_type"] = ("продажа" if op_type == "Продам" else "аренда")
                payload["price"] = int(row.get("Price", 10))
                try: 
                    payload["city"] = row.get("Address", "o, Не указано").split(",")[1].strip()
                except:
                    message += f"Не удалось обработать объявление с id: {row.get('Id', 'id не найдено')}, не найден город: задайте город вторым в адресе(область, город)\n"
                    continue
                payload["area"] = None
                payload["street"] = ""
                payload["house_number"] = ""
                payload["apartment_numder"] = ""
                rooms = row.get("Rooms", "1")
                payload["rooms"] = get_rooms(rooms)
                payload["balcony"] = bool(len(row.get("BalconyOrLoggiaMulti", "")) > 0)
                payload["renovated"] = "Да" if row.get("MarketType", "Вторичка") == "Вторичка" else "Нет"
                payload["total_area"] = int(float(row.get("Square", "0")))
                payload["floor"] = int(row.get("Floor", "1"))
                payload["total_floors"] = int(row.get("Floors", "1"))
                payload["deposit"] = int(row.get("DepositAmount", "0"))
                payload["description"] = row.get("Description", "")

                image_urls = str(row.get("ImageUrls", "")).split('|')

                image_urls = image_urls[:10]

                logger.info(f"got property: {payload}, images: {image_urls}")

                database_client = get_database_service_client()
                respond = await database_client.new_property(user_id, payload)
                property_id = respond["property_id"]

                count = 0
                for image_url in image_urls:
                    logger.info(f"Uploading image for property {property_id}")
                    image = await get_image(image_url)
                    await database_client.upload_image(property_id, count, image)
                    count += 1

                message += f"Объект {row.get('Id', 'id не найдено')} успешно загружен.\n"

                for user in respond["users_id"]:
                    message = "Посмотрите на новое объявление, подъодящее под ваши фильтры!"
                    buttons = [ 
                        [Button.inline("Связаться с риелтором 🤝", f"like:-:{property_id}")],
                        [Button.inline("В избранное ❤️", f"to_favorites:{property_id}")],
                        [Button.inline("В меню", "/start")]
                    ]

                    await send_property_info(self.client, user["telegram_id"], property_id, message=message, buttons=buttons)
                    await database_client.increase_statistics(property_id, "views")                
            except Exception as e:
                logger.info(f"Error loading property by file: {e}")
                database_client = get_database_service_client()
                respond = await database_client.delete_property(property_id)
                message += f"Не удалось обработать объявление с id: {row.get('Id', 'id не найдено')}\n"

            await self.client.send_message(user_id, message)
            await go_to_neutral_state(user_id, self.client)



