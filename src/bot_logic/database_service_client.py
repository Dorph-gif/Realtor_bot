import requests
from requests.exceptions import RequestException
import logging
import os
from io import BytesIO
from fastapi import UploadFile
import io
import aiohttp

LOG_FILE = os.path.join("logs", "bot.log")

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename=LOG_FILE,
)
logger = logging.getLogger(__name__)


class BaseHTTPClient:
    def __init__(self, base_url: str):
        self.base_url = base_url

    def _build_url(self, path: str) -> str:
        return f"{self.base_url}{path}"

    def _handle_response(self, response: requests.Response) -> dict:
        try:
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as err:
            logger.error(f"HTTP error: {err}")
            raise
        except requests.exceptions.JSONDecodeError as err:
            logger.error(f"Json decode error: {err}")
            raise

    def get(self, path: str, params: dict = None) -> dict:
        url = self._build_url(path)
        try:
            response = requests.get(url, params=params)
            return self._handle_response(response)
        except RequestException as err:
            logger.error(f"get request exception: {err}")
            raise

    def post(self, path: str, json: dict = None) -> dict:
        url = self._build_url(path)
        try:
            response = requests.post(url, json=json)
            return self._handle_response(response)
        except RequestException as err:
            logger.error(f"post request exception: {err}")
            raise

    def put(self, path: str, json: dict) -> dict:
        url = self._build_url(path)
        try:
            response = requests.put(url, json=json)
            return self._handle_response(response)
        except RequestException as err:
            logger.error(f"put request exception: {err}")
            raise

    def delete(self, path: str, params: dict) -> dict:
        url = self._build_url(path)
        try:
            response = requests.delete(url, params=params)
            return self._handle_response(response)
        except RequestException as err:
            logger.error(f"delete request exception: {err}")
            raise

class DatabaseServiceClient(BaseHTTPClient):
    def __init__(self, base_url: str = "http://db_service:8005"):
        super().__init__(base_url)

    # ----------------- User methods -----------------

    async def new_property_filter(self, user_id: int, filter: dict):
        path="/create_filter"
        payload = filter.copy()
        payload["telegram_id"] = user_id
        logger.info(f"Create new filter for user {user_id}: {filter}")
        logger.info(f"Payload: {payload}")
        return self.post(path, json=payload)

    async def update_property_filter(self, user_id: int, filter_id: int, update_param: str, new_value: str, type: str):
        path="/update_filter"
        payload = {
            "telegram_id": user_id,
            "filter_id": filter_id,
            "filter_param": update_param,
            "value": new_value,
            "type": type
        }
        logger.info(f"Update filter {filter_id} for user {user_id}: {update_param} = {new_value}")
        logger.info(f"Payload: {payload}")
        return self.post(path, json=payload)

    async def get_property_filters_list(self, user_id):
        path="/get_filters"
        payload = {
            "telegram_id": user_id
        }
        return self.get(path, params=payload)
    
    async def get_property_filter(self, filter_id: int):
        path="/get_filter"
        payload = {
            "filter_id": filter_id
        }
        return self.get(path, params=payload)

    async def delete_property_filter(self, user_id, filter_id: int):
        path="/delete_filter"
        payload = {
            "telegram_id": user_id,
            "filter_id": filter_id
        }
        return self.delete(path, params=payload)

    async def get_favorites_list(self, user_id: int, offset: int, limit: int = 10):
        path=f"/get_favorites/{user_id}/{offset}/{limit}"
        logger.info(f"Get favorites list for user {user_id}")
        return self.get(path)
    
    async def delete_from_favorites(self, favorites_id: int):
        path="/delete_from_favorites"
        payload = {
            "favorites_id": favorites_id
        }
        logger.info(f"Delete from favorites {favorites_id}")
        logger.info(f"Payload: {payload}")
        return self.delete(path, params=payload)

    async def get_next_announcement(self, filter_id: int):
        path="/get_property_for_filter"
        payload = {
            "filter_id": filter_id
        }
        logger.info(f"Get next announcement for filter {filter_id}")
        logger.info(f"Payload: {payload}")
        return self.get(path, params=payload)

    async def add_to_favorites(self, user_id: int, property_id: int):
        path = f"/add_to_favorites/{user_id}/{property_id}"

        self.post(path=path)

    async def increase_statistics(self, property_id: int, param_name: str):
        path="/increase_statistics"

        payload={
            "property_id":property_id,
            "param_name":param_name
        }

        self.post(path, json=payload)

    # ----------------- Admin methods -----------------

    async def is_admin(self, user_id: int):
        path="/is_admin"
        payload = {
            "telegram_id": user_id
        }
        return self.get(path, params=payload)["is_admin"]

    async def register_admin(self, user_id: int):
        path="/register_admin"+f"/{user_id}"
        payload = {
            "telegram_id": user_id,
        }
        logger.info(f"Register admin {user_id}")
        logger.info(f"Payload: {payload}")
        return self.post(path, json=payload)

    async def unregister_admin(self, user_id: int):
        path=f"/unregister_admin/{user_id}"
        logger.info(f"Unregister admin {user_id}")
        return self.post(path)

    async def new_property(self, user_id: int, property: dict):
        path="/add_property"
        payload = property.copy()
        payload["telegram_id"] = user_id
        return self.post(path, json=payload)

    async def upload_image(self, property_id: int, number: int, image_bytes: bytes):
        path=f"/upload_image"
        logger.info(f"Upload image for property {property_id}")
        try:
            file = { "image": (f"{property_id}_{number}.jpeg", image_bytes, "image/jpeg") }
            """
            file = io.BytesIO(image_bytes)
            file.seek(0)
            file.name = f"{property_id}_{number}.jpeg"

            files = { "image"}
            """
            response = requests.post(self._build_url(path), files=file)
        except Exception as e:
            logger.error(f"Ошибка при отправке изображения в FastAPI: {e}")
            return None

    async def get_property_description(self, property_id: int):
        path = f"/get_property_info/{property_id}"
        return self.get(path)

    async def get_property_photo(self, property_id: int, photo_num: int = 0):
        path = f"/properties/{property_id}/photo/{photo_num}"

        try:
            response = requests.get(self._build_url(path))
            response.raise_for_status()
            return response.content
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching photo {photo_num} for property {property_id}: {e}")
            return None
        except requests.exceptions.HTTPError as e:
            logger.error(f"HTTP error fetching photo {photo_num} for property {property_id}: {e}")
            return None
        except requests.exceptions.JSONDecodeError as e:
            logger.error(f"JSON decode error fetching photo {photo_num} for property {property_id}: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error fetching photo {photo_num} for property {property_id}: {e}")
            return None

    async def get_property_photos(self, property_id: int):
        path = f"/get_property_photos_count/{property_id}"
        count = self.get(path)

        if count is None:
            logger.error(f"Failed to get photo count for property {property_id}")
            return []
        
        count = count.get("photos_count", 0)
        if count == 0:
            logger.info(f"No photos found for property {property_id}")
            return []
        logger.info(f"Found {count} photos for property {property_id}")

        photos = []

        for photo_num in range(count):

            photo_bytes = await self.get_property_photo(property_id, photo_num)

            if photo_bytes is None:
                logger.error(f"Failed to get photo {photo_num} for property {property_id}")
                continue

            logger.info(f"Got photo {photo_num} for property {property_id}")

            photos.append(photo_bytes) 

        return photos
        
    async def get_property_list(self, offset: int, limit: int):
        path = f"/get_properties/{offset}/{limit}"

        return self.get(path)

    async def delete_property(self, property_id: int):
        path = f"/delete_property/{property_id}"
        logger.info(f"Delete property {property_id}")
        return self.delete(path, params={})

    async def change_property_state(self, property_id: int, new_state: str):
        path = f"/change_property_state/{property_id}/{new_state}"
        logger.info(f"Change property state {property_id}")
        payload = {
            "new_state": new_state
        }
        return self.post(path, json=payload)

    async def get_property_statistics(self, property_id: int):
        path = f"/get_property_statistics/{property_id}"

        return self.get(path)
    
    async def get_statistics(self):
        path = f"/get_statistics"

        return self.get(path)

def get_database_service_client(base_url: str = "http://db_service:8005") -> DatabaseServiceClient:
    return DatabaseServiceClient(base_url=base_url)
