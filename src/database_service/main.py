from fastapi import FastAPI, HTTPException, Depends, UploadFile, File, status
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import uvicorn
import json
import os
import logging
from typing import Optional, List
from dotenv import load_dotenv
import uuid
from typing import Annotated
import os
from io import BytesIO
from fastapi.responses import FileResponse, Response

from src.database_service.db_manager import get_database_manager, SqlDatabaseManager
from src.database_service.create_tables import create_tables
load_dotenv()

LOG_FILE = os.path.join("logs", "database_service.log")

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename=LOG_FILE,
)
logger = logging.getLogger(__name__)

app = FastAPI()

class AddFilterRequest(BaseModel):
    telegram_id: int
    name: Optional[str] = None
    property_type: Optional[str] = None
    deal_type: Optional[str] = None
    city: Optional[str] = None
    areas: Optional[str] = None
    min_price: Optional[int] = None
    max_price: Optional[int] = None
    min_rooms: Optional[int] = None
    max_rooms: Optional[int] = None
    min_total_area: Optional[float] = None
    max_total_area: Optional[float] = None
    balcony: Optional[bool] = None
    renovated: Optional[str] = None
    min_deposit: Optional[int] = None
    max_deposit: Optional[int] = None
    floor: Optional[int] = None
    is_active: Optional[bool] = True
    total_floors: Optional[int] = None

class UpdateFilter(BaseModel):
    telegram_id: int
    filter_id: int
    filter_param: str
    value: str
    type: str

class Property(BaseModel):
    return_contact: str
    property_type: str
    deal_type: str
    price: int
    city: str = None
    area: str = None
    street: Optional[str] = None
    house_number: Optional[str] = None
    apartment_number: Optional[str] = None
    rooms: Optional[int] = None
    balcony: Optional[bool] = False
    renovated: Optional[str] = None
    total_area: Optional[int] = None
    floor: Optional[int] = None
    total_floors: Optional[int] = None
    deposit: Optional[int] = None
    description: Optional[str] = None

class IncreaseStatistics(BaseModel):
    property_id: int
    param_name: str

# ---------------------- User Endpoints ------------------

@app.post("/create_filter")
async def create_filter(
    filter: AddFilterRequest,
    database_manager : SqlDatabaseManager = Depends(get_database_manager)
):
    try:
        telegram_id = filter.telegram_id

        if not telegram_id:
            raise HTTPException(status_code=400, detail="User ID is required")

        await database_manager.add_filter(filter)

        return {"status": "ok", "telegram_id": telegram_id}
    except Exception as e:
        logger.exception(f"Failed to create subscription: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    
@app.post("/update_filter")
async def update_filter(
    params: UpdateFilter,
    database_manager : SqlDatabaseManager = Depends(get_database_manager)
):
    telegram_id = params.telegram_id
    filter_id = params.filter_id
    filter_param = params.filter_param
    value = params.value
    param_type = params.type

    if param_type == "int":
        try:
            value = int(value)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid value for integer parameter")
    elif param_type == "bool":
        if value.lower() == "true":
            value = True
        elif value.lower() == "false":
            value = False
        else:
            raise HTTPException(status_code=400, detail="Invalid value for boolean parameter")
    elif param_type == "list":
        value = json.dumps([element.strip() for element in value.split(",")])
        await database_manager.update_filter_list_param(telegram_id, filter_id, filter_param, value)

        return {"status": "ok", "telegram_id": telegram_id}
    
    try:
        if not telegram_id:
            raise HTTPException(status_code=400, detail="User ID is required")

        await database_manager.update_filter(telegram_id, filter_id, filter_param, value)

        return {"status": "ok", "telegram_id": telegram_id}
    except Exception as e:
        logger.exception(f"Failed to create subscription: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    
@app.delete("/delete_filter")
async def delete_filter(
    telegram_id: int,
    filter_id: int,
    database_manager : SqlDatabaseManager = Depends(get_database_manager)
):
    try:
        if not telegram_id:
            raise HTTPException(status_code=400, detail="User ID is required")

        await database_manager.delete_filter(telegram_id, filter_id)

        return {"status": "ok", "telegram_id": telegram_id}
    except Exception as e:
        logger.exception(f"Failed to create subscription: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/get_filters")
async def get_filters(
    telegram_id: int,
    database_manager : SqlDatabaseManager = Depends(get_database_manager)
):
    try:
        filters = await database_manager.get_filters(telegram_id)
        return filters
    except Exception as e:
        logger.exception(f"Failed to get filters: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/get_filter")
async def get_filters(
    filter_id: int,
    database_manager : SqlDatabaseManager = Depends(get_database_manager)
):
    try:
        filter_info = await database_manager.get_filter(filter_id)
        return filter_info
    except Exception as e:
        logger.exception(f"Failed to get filter_info: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/get_property_for_filter")
async def get_property_for_filter(
    filter_id: int,
    database_manager : SqlDatabaseManager = Depends(get_database_manager)
):
    try:
        property_id = await database_manager.get_property_for_filter(filter_id)
        return property_id
    except Exception as e:
        logger.exception(f"Failed to get filters: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/add_to_favorites/{telegram_id}/{property_id}")
async def add_to_favorites(
    telegram_id: int,
    property_id: int,
    database_manager : SqlDatabaseManager = Depends(get_database_manager)
):
    try:
        if not telegram_id:
            raise HTTPException(status_code=400, detail="User ID is required")

        await database_manager.add_to_favorites(telegram_id, property_id)

        return {"status": "ok", "telegram_id": telegram_id}
    except Exception as e:
        logger.exception(f"Failed to add to favorites: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/remove_from_favorites")
async def remove_from_favorites(
    favorites_id: int,
    database_manager : SqlDatabaseManager = Depends(get_database_manager)
):
    try:
        if not favorites_id:
            raise HTTPException(status_code=400, detail="ID is required")

        await database_manager.remove_from_favorites(favorites_id)

        return {"status": "ok", "favorites_id": favorites_id}
    except Exception as e:
        logger.exception(f"Failed to remove from favorites: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/get_favorites/{telegram_id}/{offset}/{limit}")
async def get_favorites(
    telegram_id: int,
    offset: int,
    limit: int,
    database_manager : SqlDatabaseManager = Depends(get_database_manager)
):
    try:
        if not telegram_id:
            raise HTTPException(status_code=400, detail="User ID is required")

        favorites = await database_manager.get_favorites(telegram_id, offset, limit)

        return favorites
    except Exception as e:
        logger.exception(f"Failed to get favorites: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/increase_statistics")
async def increase_statistics(
    params:IncreaseStatistics,
    database_manager : SqlDatabaseManager = Depends(get_database_manager)
):
    try:
        if not params.telegram_id:
            raise HTTPException(status_code=400, detail="User ID is required")

        favorites = await database_manager.increase_statistics(params.telegram_id, params.property_id, params.param_name)

        return favorites
    except Exception as e:
        logger.exception(f"Failed to increase statistics: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ---------------------- Admin Endpoints ------------------

IMAGE_UPLOAD_FOLDER = os.getenv("IMAGE_UPLOAD_FOLDER", "/ad_images")

@app.get("/is_admin")
async def is_admin(
    telegram_id: int,
    database_manager : SqlDatabaseManager = Depends(get_database_manager)
):
    try:
        is_admin = await database_manager.is_admin(telegram_id)
        return {"is_admin": is_admin}
    except Exception as e:
        logger.exception(f"Failed to check admin status: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    
@app.post("/register_admin/{telegram_id}")
async def register_admin(
    telegram_id: int,
    database_manager : SqlDatabaseManager = Depends(get_database_manager)
):
    try:
        if not telegram_id:
            raise HTTPException(status_code=400, detail="User ID is required")

        await database_manager.register_admin(telegram_id)

        return {"status": "ok", "telegram_id": telegram_id}
    except Exception as e:
        logger.exception(f"Failed to register admin: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/unregister_admin/{telegram_id}")
async def unregister_admin(
    telegram_id: int,
    database_manager : SqlDatabaseManager = Depends(get_database_manager)
):
    try:
        if not telegram_id:
            raise HTTPException(status_code=400, detail="User ID is required")

        await database_manager.unregister_admin(telegram_id)

        return {"status": "ok", "telegram_id": telegram_id}
    except Exception as e:
        logger.exception(f"Failed to unregister admin: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/upload_image")
async def upload_images(image: UploadFile = File(...), database_manager : SqlDatabaseManager = Depends(get_database_manager)):
    try:
        logger.info(f"Uploading image: {image}")

        filename = image.filename
        file_extension = filename.split(".")[-1]

        filepath = os.path.join(IMAGE_UPLOAD_FOLDER, filename)

        contents = await image.read()

        logger.info(f"Image filename: {filename} file_extension: {file_extension}")

        with open(filepath, "wb") as f:
            f.write(contents)

        logger.info(f"Image saved to {filepath}")

        if not image.filename:
            raise HTTPException(status_code=400, detail="Отсутствует имя файла изображения")

        try:
            property_id = int(filename.split("_")[0])
            if not property_id:
                raise HTTPException(status_code=400, detail="Отсутствует ID объявления в имени файла")
        except ValueError:
            raise HTTPException(status_code=400, detail="Неверный формат имени файла. Ожидается <property_id>_<number>.jpg")

        logger.info(f"Uploading image property_id: {property_id}")

        await database_manager.upload_image(filepath, property_id)

        return {"status": "ok"}
    except HTTPException as e:
        logger.exception(f"Failed to upload image: {e.detail}")

        raise e
    except Exception as e:
        logger.exception(f"Failed to upload image: {e}")
        raise HTTPException(status_code=500, detail=f"Произошла общая ошибка: {e}")

@app.post("/add_property")
async def add_property(
    property: Property,
    database_manager : SqlDatabaseManager = Depends(get_database_manager)
):
    try:
        property_id = await database_manager.add_property(property)
        users_id = await database_manager.get_filters_for_property(property)

        return {"status": "ok" , "property_id": property_id, "users_id": users_id}
    except Exception as e:
        logger.exception(f"Failed to add property: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/get_properties/{offset}/{limit}")
async def get_properties(
    offset: int = 0,
    limit: int = 10,
    database_manager : SqlDatabaseManager = Depends(get_database_manager),
):
    try:
        properties = await database_manager.get_properties(offset, limit)
        return {"properties": properties}
    except Exception as e:
        logger.exception(f"Failed to get properties: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/get_property_info/{property_id}")
async def get_property(property_id: int, database_manager : SqlDatabaseManager = Depends(get_database_manager)):
    try:
        property_data = await database_manager.get_property_details(property_id)
        if not property_data:
            raise HTTPException(status_code=404, detail="Объект недвижимости не найден")
        return property_data
    except HTTPException as e:
        logger.exception(f"Failed to get property: {e.detail}")
        raise e
    except Exception as e:
        logger.exception(f"Failed to get property: {e}")
        raise HTTPException(status_code=500, detail=f"Произошла общая ошибка: {e}")

@app.get("/get_property_photos_count/{property_id}")
async def get_property_photos_count(property_id: int, database_manager : SqlDatabaseManager = Depends(get_database_manager)):
    try:
        count = await database_manager.get_property_photos_count(property_id)
        if count is None:
            raise HTTPException(status_code=404, detail="Объект недвижимости не найден")
        return {"photos_count": count}
    except HTTPException as e:
        logger.exception(f"Failed to get property photos count: {e.detail}")
        raise e
    except Exception as e:
        logger.exception(f"Failed to get property photos count: {e}")
        raise HTTPException(status_code=500, detail=f"Произошла общая ошибка: {e}")

@app.get("/properties/{property_id}/photo/{photo_num}")
async def get_property_photo(property_id: int, photo_num: int,
    database_manager : SqlDatabaseManager = Depends(get_database_manager)
):
    photo_path = await database_manager.get_property_photo_path(property_id, photo_num)

    if not photo_path:
        raise HTTPException(status_code=404, detail="Фотография не найдена")

    if not os.path.exists(photo_path):
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Фотография не найдена на сервере")

    with open(photo_path, "rb") as f:
        image_bytes = f.read()

    return Response(content=image_bytes, media_type="image/jpeg")

@app.delete("/delete_property/{property_id}")
async def delete_property(
    property_id: int,
    database_manager : SqlDatabaseManager = Depends(get_database_manager)
):
    try:
        if not property_id:
            raise HTTPException(status_code=400, detail="ID is required")

        await database_manager.delete_property(property_id)

        return {"status": "ok", "property_id": property_id}
    except Exception as e:
        logger.exception(f"Failed to delete property: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/change_property_state/{property_id}/{new_state}")
async def change_property_state(
    property_id: int,
    new_state: str,
    database_manager : SqlDatabaseManager = Depends(get_database_manager)
):
    try:
        if not property_id:
            raise HTTPException(status_code=400, detail="ID is required")

        await database_manager.change_property_state(property_id, new_state)

        return {"status": "ok", "property_id": property_id}
    except Exception as e:
        logger.exception(f"Failed to change property state: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/get_property_statistics/{property_id}")
async def get_property_statistics(
    property_id: int = 0,
    database_manager : SqlDatabaseManager = Depends(get_database_manager),
):
    try:
        statistics = await database_manager.get_property_statistics(property_id)
        return statistics
    except Exception as e:
        logger.exception(f"Failed to get property statistics: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    
@app.get("/get_statistics")
async def get_statistics(
    database_manager : SqlDatabaseManager = Depends(get_database_manager),
):
    try:
        statistics = await database_manager.get_statistics()
        return statistics
    except Exception as e:
        logger.exception(f"Failed to get statistics: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    create_tables()
    uvicorn.run(app, host="0.0.0.0", port=8005)