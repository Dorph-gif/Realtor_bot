import asyncpg
from typing import List, Dict
import json

import logging
from dotenv import load_dotenv
import os

load_dotenv()

DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")

LOG_FILE = os.path.join("logs", "daatbase_service.log")

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename=LOG_FILE,
)
logger = logging.getLogger(__name__)

DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

async def get_database_manager():
    database_manager = SqlDatabaseManager(DATABASE_URL)
    await database_manager.connect()
    try:
        yield database_manager
    finally:
        await database_manager.disconnect()

class SqlDatabaseManager:
    def __init__(self, database_url: str):
        self.database_url = database_url
        self.pool = None

    async def connect(self):
        try:
            self.pool = await asyncpg.create_pool(self.database_url)
            logger.info("Connected to the database")
        except Exception as e:
            logger.exception(f"Failed to connect to the database: {e}")
            raise

    async def disconnect(self):
        if self.pool:
            await self.pool.close()
            logger.info("Disconnected from the database")

    # ------------------ User Functions ------------------

    async def check_user(self, conn, telegram_id: int):
        async with self.pool.acquire() as conn:
            try:
                result = await conn.fetchrow("SELECT * FROM users WHERE telegram_id = $1", telegram_id)
                
                if not result:
                    await conn.execute("INSERT INTO users (telegram_id) VALUES ($1)", telegram_id)
                    logger.info(f"User with telegram_id {telegram_id} added to the database")
                    return False
                
            except Exception as e:
                logger.exception(f"Failed to check user: {e}")
                raise

    async def add_filter(self, filter_data):
        async with self.pool.acquire() as conn:
            try:
                telegram_id = (filter_data.telegram_id)

                await self.check_user(conn, telegram_id)

                query = """
                    INSERT INTO user_property_preferences (
                        telegram_id, name, property_type, deal_type, city, areas,
                        min_price, max_price, min_rooms, max_rooms, min_total_area,
                        max_total_area, balcony, renovated, min_deposit, max_deposit,
                        floor, is_active, total_floors
                    ) VALUES (
                        $1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15, $16, $17, $18, $19
                    )
                """

                values = (
                    filter_data.telegram_id,
                    filter_data.name,
                    filter_data.property_type,
                    filter_data.deal_type,
                    filter_data.city,
                    json.dumps([element.strip() for element in filter_data.areas.split(",")]),
                    filter_data.min_price,
                    filter_data.max_price,
                    filter_data.min_rooms,
                    filter_data.max_rooms,
                    filter_data.min_total_area,
                    filter_data.max_total_area,
                    filter_data.balcony,
                    filter_data.renovated,
                    filter_data.min_deposit,
                    filter_data.max_deposit,
                    filter_data.floor,
                    filter_data.is_active,
                    filter_data.total_floors,
                )

                await conn.execute(query, *values)
                logger.info(f"Added filter for telegram_id: {filter_data.telegram_id}")

            except Exception as e:
                logger.exception(f"Failed to add filter: {e}")
                raise

    async def update_filter(self, telegram_id: int, filter_id: int, filter_param: str, value):
        async with self.pool.acquire() as conn:
            try:
                await self.check_user(conn, telegram_id)
                query = f"UPDATE user_property_preferences SET {filter_param.lower()} = $1 WHERE id = $2"
                await conn.execute(query, value, filter_id)
                logger.info(f"Updated filter {filter_id} for telegram_id: {telegram_id}")

            except Exception as e:
                logger.exception(f"Failed to update filter: {e}")
                raise

    async def update_filter_list_param(self, telegram_id: int, filter_id: int, filter_param: str, value):
        async with self.pool.acquire() as conn:
            try:
                await self.check_user(conn, telegram_id)
                query = f"UPDATE user_property_preferences SET {filter_param.lower()} = $1::jsonb WHERE id = $2"
                await conn.execute(query, value, filter_id)
                logger.info(f"Updated filter {filter_id} for telegram_id: {telegram_id}")

            except Exception as e:
                logger.exception(f"Failed to update filter: {e}")
                raise

    async def delete_filter(self, telegram_id: int, filter_id: int):
        async with self.pool.acquire() as conn:
            try:
                await self.check_user(conn, telegram_id)
                await conn.execute("DELETE FROM user_property_preferences WHERE id = $1", filter_id)
                logger.info(f"Deleted filter {filter_id}")
            except Exception as e:
                logger.exception(f"Failed to delete filter {filter_id}: {e}")
                raise

    async def get_filters(self, telegram_id: int) -> List[Dict]:
        async with self.pool.acquire() as conn:
            try:
                await self.check_user(conn, telegram_id)
                filters = await conn.fetch("SELECT name, id FROM user_property_preferences WHERE telegram_id = $1", telegram_id)
                return [dict(filter) for filter in filters]
            except Exception as e:
                logger.exception(f"Failed to get filters: {e}")
                raise

    async def get_filter(self, filter_id: int) -> List[Dict]:
        async with self.pool.acquire() as conn:
            try:
                await self.check_user(conn, filter_id)
                filter_info = await conn.fetch("SELECT * FROM user_property_preferences WHERE id = $1", filter_id)

                if filter_info:
                    return dict(filter_info[0])
                else:
                    return None

            except Exception as e:
                logger.exception(f"Failed to get filters: {e}")
                raise

    async def add_to_favorites(self, telegram_id: int, property_id: int):
        async with self.pool.acquire() as conn:
            try:
                await conn.execute("INSERT INTO user_favorites (telegram_id, property_id) VALUES ($1, $2)", telegram_id, property_id)
                logger.info(f"Added property {property_id} to favorites for user {telegram_id}")
            except Exception as e:
                logger.exception(f"Failed to add property to favorites: {e}")
                raise

    async def remove_from_favorites(self, favorites_id: int):
        async with self.pool.acquire() as conn:
            try:
                await conn.execute("DELETE FROM user_favorites WHERE id = $1", favorites_id)
                logger.info(f"Removed property {favorites_id} from favorites")
            except Exception as e:
                logger.exception(f"Failed to remove property from favorites: {e}")
                raise

    async def get_favorites(self, telegram_id: int, offset: int, limit: int):
        async with self.pool.acquire() as conn:
            try:
                query = """
                    SELECT id, property_id
                    FROM user_favorites
                    WHERE telegram_id = $1
                    OFFSET $2 LIMIT $3
                """
                favorites = await conn.fetch(query, telegram_id, offset, limit)
                return [dict(favorite) for favorite in favorites]
            except Exception as e:
                logger.exception(f"Failed to get favorites: {e}")
                raise

    async def get_property_for_filter(self, filter_id: int):

        async with self.pool.acquire() as conn:
            try:
                logger.info(f"Получение объекта недвижимости для фильтра {filter_id}")
                query = """
                    SELECT 
                        property_type, deal_type, city, areas, min_price, max_price, 
                        min_rooms, max_rooms, min_total_area, max_total_area, balcony, 
                        renovated, min_deposit, max_deposit, floor, total_floors
                    FROM user_property_preferences
                    WHERE id = $1;
                """
                filter_data = await conn.fetchrow(query, filter_id)
                logger.info(f"Полученные данные фильтра: {filter_data}")

                if not filter_data:
                    logger.warning(f"Фильтр с ID {filter_id} не найден или не активен.")
                    return None


                where_clauses = []
                params = {}

                where_clauses.append("state = $1")
                params["state"] = "Активно"
                param_index = 2

                where_clauses.append(f"property_type = ${param_index}")
                params["property_type"] = filter_data["property_type"]
                param_index += 1

                where_clauses.append(f"deal_type = ${param_index}")
                params["deal_type"] = filter_data["deal_type"]
                param_index += 1

                where_clauses.append(f"city = ${param_index}")
                params["city"] = filter_data["city"]
                param_index += 1

                areas = filter_data["areas"]
                if areas:
                    where_clauses.append(f"area = ANY(${param_index})")
                    params["areas"] = list(areas)
                    param_index += 1

                if filter_data["min_price"] is not None:
                    where_clauses.append(f"price >= ${param_index}")
                    params["min_price"] = filter_data["min_price"]
                    param_index += 1
                if filter_data["max_price"] is not None:
                    where_clauses.append(f"price <= ${param_index}")
                    params["max_price"] = filter_data["max_price"]
                    param_index += 1

                if filter_data["min_rooms"] is not None:
                    where_clauses.append(f"rooms >= ${param_index}")
                    params["min_rooms"] = filter_data["min_rooms"]
                    param_index += 1
                if filter_data["max_rooms"] is not None:
                    where_clauses.append(f"rooms <= ${param_index}")
                    params["max_rooms"] = filter_data["max_rooms"]
                    param_index += 1

                if filter_data["min_total_area"] is not None:
                    where_clauses.append(f"total_area >= ${param_index}")
                    params["min_total_area"] = filter_data["min_total_area"]
                    param_index += 1
                if filter_data["max_total_area"] is not None:
                    where_clauses.append(f"total_area <= ${param_index}")
                    params["max_total_area"] = filter_data["max_total_area"]
                    param_index += 1

                if filter_data["balcony"] is not None:
                    where_clauses.append(f"balcony = ${param_index}")
                    params["balcony"] = filter_data["balcony"]
                    param_index += 1

                if filter_data["renovated"]:
                  where_clauses.append(f"renovated = ${param_index}")
                  params["renovated"] = filter_data["renovated"]
                  param_index += 1

                if filter_data["min_deposit"] is not None:
                    where_clauses.append(f"deposit >= ${param_index}")
                    params["min_deposit"] = filter_data["min_deposit"]
                    param_index += 1
                if filter_data["max_deposit"] is not None:
                    where_clauses.append(f"deposit <= ${param_index}")
                    params["max_deposit"] = filter_data["max_deposit"]
                    param_index += 1

                if filter_data["floor"] is not None:
                    where_clauses.append(f"floor = ${param_index}")
                    params["floor"] = filter_data["floor"]
                    param_index += 1

                if filter_data["total_floors"] is not None:
                    where_clauses.append(f"total_floors = ${param_index}")
                    params["total_floors"] = filter_data["total_floors"]
                    param_index += 1

                logger.info(f"Фильтр для поиска: {where_clauses}")

                where_clause = " AND ".join(where_clauses)
                sql_query = f"""
                    SELECT id
                    FROM properties
                    WHERE {where_clause}
                    ORDER BY RANDOM()
                    LIMIT 1;
                """

                logger.info(f"SQL запрос: {sql_query}")
                logger.info(f"Параметры запроса: {params}")

                prepared_params = [params[key] for key in params]
                property_id = await conn.fetchval(sql_query, *prepared_params)

                if property_id:
                    logger.info(f"Найден случайный объект недвижимости {property_id} для фильтра {filter_id}.")
                    return property_id
                else:
                    logger.info(f"Не найдено объектов недвижимости для фильтра {filter_id}.")
                    return None

            except Exception as e:
                logger.exception(f"Ошибка при поиске объекта недвижимости: {e}")
                return None

    async def increase_statistics(self, property_id: int, param_name: str):
        async with self.pool.acquire() as conn:
            try:
                await conn.execute(f"UPDATE user_statistics SET {param_name} = {param_name} + 1 WHERE id = 1")
                await conn.execute(f"UPDATE property_statistics SET {param_name} = {param_name} + 1 WHERE property_id = {property_id}")
            except Exception as e:
                logger.exception(f"Failed to add property to favorites: {e}")
                raise

    # ------------------ Admin Functions ------------------

    async def is_admin(self, telegram_id: int) -> bool:
        async with self.pool.acquire() as conn:
            try:
                result = await conn.fetchrow("SELECT is_admin FROM users WHERE telegram_id = $1", telegram_id)

                if not result:
                    result = False

                return bool(result["is_admin"])
            except Exception as e:
                logger.exception(f"Failed to check admin status: {e}")
                raise

    async def register_admin(self, telegram_id: int):
        async with self.pool.acquire() as conn:
            try:
                result = await conn.fetchrow("SELECT * FROM users WHERE telegram_id = $1", telegram_id)

                if not result:
                    await conn.execute("INSERT INTO users (telegram_id, is_admin) VALUES ($1, TRUE)", telegram_id)
                    logger.info(f"Admin with telegram_id {telegram_id} added to the database")
                else:
                    await conn.execute("UPDATE users SET is_admin = TRUE WHERE telegram_id = $1", telegram_id)
                    logger.info(f"Admin with telegram_id {telegram_id} already exists in the database")

            except Exception as e:
                logger.exception(f"Failed to register admin: {e}")
                raise

    async def unregister_admin(self, telegram_id: int):
        async with self.pool.acquire() as conn:
            try:
                result = await conn.fetchrow("SELECT * FROM users WHERE telegram_id = $1", telegram_id)

                if not result:
                    logger.info(f"Admin with telegram_id {telegram_id} not found in the database")
                else:
                    await conn.execute("UPDATE users SET is_admin = FALSE WHERE telegram_id = $1", telegram_id)
                    logger.info(f"Admin with telegram_id {telegram_id} removed from the database")

            except Exception as e:
                logger.exception(f"Failed to unregister admin: {e}")
                raise

    async def get_filters_for_property(self, property):
        async with self.pool.acquire() as conn:
            query = """
            SELECT telegram_id 
            FROM user_property_preferences 
            WHERE is_active = TRUE
            """
            params = []

            if property.property_type:
                query += " AND (property_type IS NULL OR property_type = $1)"
                params.append(property.property_type)

            if property.deal_type:
                query += " AND (deal_type IS NULL OR deal_type = $2)"
                params.append(property.deal_type)

            if property.city:
                query += " AND (city IS NULL OR city = $3)"
                params.append(property.city)

            if property.area:
                query += " AND (areas IS NULL OR areas @> $4::jsonb)"
                params.append(json.dumps(property.area))

            if property.rooms is not None:
                query += " AND (min_rooms IS NULL OR max_rooms IS NULL OR (min_rooms <= $5 AND max_rooms >= $5))"
                params.append(property.rooms)

            if property.price is not None:
                query += " AND (min_price IS NULL OR max_price IS NULL OR (min_price <= $6 AND max_price >= $6))"
                params.append(property.price)

            if property.balcony is not None:
                query += " AND (balcony IS NULL OR balcony = $7)"
                params.append(property.balcony)

            if property.renovated:
                query += " AND (renovated IS NULL OR renovated = $8)"
                params.append(property.renovated)

            if property.total_area is not None:
                query += " AND (min_total_area IS NULL OR max_total_area IS NULL OR (min_total_area <= $9 AND max_total_area >= $9))"
                params.append(property.total_area)

            if property.floor is not None:
                query += " AND (floor IS NULL OR floor = $10)"
                params.append(property.floor)

            if property.total_floors is not None:
                query += " AND (total_floors IS NULL OR total_floors = $11)"
                params.append(property.total_floors)

            if property.deposit is not None:
                query += " AND (min_deposit IS NULL OR max_deposit IS NULL OR (min_deposit <= $12 AND max_deposit >= $12))"
                params.append(property.deposit)

            filters = await conn.fetch(query, *params)

            return filters

    async def add_property(self, property_data):
        async with self.pool.acquire() as conn:
            try:
                query = """
                    INSERT INTO properties (
                        return_contact, property_type, deal_type, price, city, area, street,
                        house_number, apartment_number, rooms, balcony,
                        renovated, total_area, floor, total_floors, deposit, description
                    ) VALUES (
                        $1, $2, $3, $4, $5, $6,
                        $7, $8, $9, $10, $11, $12, $13, $14, $15, $16, $17
                    )
                    RETURNING id
                """

                values = (
                    property_data.return_contact,
                    property_data.property_type,
                    property_data.deal_type,
                    property_data.price,
                    property_data.city,
                    property_data.area,
                    property_data.street,
                    property_data.house_number,
                    property_data.apartment_number,
                    property_data.rooms,
                    property_data.balcony,
                    property_data.renovated,
                    property_data.total_area,
                    property_data.floor,
                    property_data.total_floors,
                    property_data.deposit,
                    property_data.description,
                )

                property_id = await conn.fetchval(query, *values)
                await conn.execute("INSERT INTO property_statistics (property_id) VALUES ($1)", property_id)
                return property_id

            except Exception as e:
                logger.exception(f"Failed to add new property: {e}")
                raise

    async def upload_image(self, path: str, property_id: int):
        async with self.pool.acquire() as conn:
            try:
                await conn.execute("INSERT INTO property_photos (photo_path, property_id) VALUES ($1, $2)", path, property_id)
                logger.info(f"Added image {path} for property_id: {property_id}")
            except Exception as e:
                logger.exception(f"Failed to add image: {e}")
                raise

    async def get_property_details(self, property_id: int):
            async with self.pool.acquire() as conn:
                try:
                    query = """
                        SELECT id, state, return_contact, description, property_type, deal_type, price, city, area, street,
                            house_number, apartment_number, rooms, balcony, renovated, total_area, floor, total_floors, deposit,
                            created_at, updated_at
                        FROM properties
                        WHERE id = $1
                    """
                    row = await conn.fetchrow(query, property_id)

                    if row:
                        return dict(row)
                    else:
                        return None
                except Exception as e:
                    logger.exception(f"Failed to add new property: {e}")
                    raise

    async def get_property_photos_count(self, property_id: int):
            async with self.pool.acquire() as conn:
                try:
                    query = """
                        SELECT COUNT(*) AS photo_count
                        FROM property_photos
                        WHERE property_id = $1
                    """
                    
                    result = await conn.fetchval(query, property_id)

                    return result
                except Exception as e:
                    logger.exception(f"Failed to get photos count: {e}")
                    raise

    async def get_property_photo_path(self, property_id: int, photo_num: int):
            async with self.pool.acquire() as conn:
                try:
                    query = """
                        SELECT photo_path
                        FROM property_photos
                        WHERE property_id = $1
                        ORDER BY id
                        LIMIT 1
                        OFFSET $2
                    """
                    result = await conn.fetchrow(query, property_id, photo_num)

                    return result['photo_path']
                except Exception as e:
                    logger.exception(f"Failed to add new property: {e}")
                    raise

    async def get_properties(self, offset: int, limit: int):
        async with self.pool.acquire() as conn:
            try:
                query = """
                    SELECT id
                    FROM properties
                    ORDER BY created_at DESC
                    OFFSET $1 LIMIT $2
                """
                properties = await conn.fetch(query, offset, limit)
                return [property for property in properties]
            except Exception as e:
                logger.exception(f"Failed to get properties: {e}")
                raise

    async def delete_property(self, property_id: int):
        async with self.pool.acquire() as conn:
            try:
                await conn.execute("DELETE FROM property_photos WHERE property_id = $1", property_id)
                await conn.execute("DELETE FROM user_favorites WHERE property_id = $1", property_id)
                await conn.execute("DELETE FROM property_statistics WHERE property_id = $1", property_id)
                await conn.execute("DELETE FROM properties WHERE id = $1", property_id)

                logger.info(f"Deleted property {property_id}")
            except Exception as e:
                logger.exception(f"Failed to delete property {property_id}: {e}")
                raise

    async def change_property_state(self, property_id: int, new_state: str):
        async with self.pool.acquire() as conn:
            try:
                await conn.execute("UPDATE properties SET state = $1 WHERE id = $2", new_state, property_id)

                logger.info(f"Changed property state {property_id}")
            except Exception as e:
                logger.exception(f"Failed to change property state {property_id}: {e}")
                raise

    async def get_property_statistics(self, property_id):
        async with self.pool.acquire() as conn:
            try:
                query = """
                    SELECT views, favorites, likes
                    FROM property_statistics 
                    WHERE property_id = $1
                """
                statistics = await conn.fetchrow(query, property_id)
                result_dict = {
                    "views": statistics[0],
                    "favorites": statistics[1],
                    "likes": statistics[2],
                }
                return result_dict
            except Exception as e:
                logger.exception(f"Failed to get properties: {e}")
                raise

    async def get_statistics(self):
        async with self.pool.acquire() as conn:
            try:
                query = """
                    SELECT views, favorites, likes
                    FROM user_statistics WHERE id = 1
                """
                statistics = await conn.fetchrow(query)
                result_dict = {
                    "views": statistics[0],
                    "favorites": statistics[1],
                    "likes": statistics[2],
                }
                return result_dict
            except Exception as e:
                logger.exception(f"Failed to get statistics: {e}")
                raise

