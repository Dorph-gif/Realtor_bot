from typing import List, Optional

import logging
import os
from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
import uvicorn
import asyncio
from src.server.scrapper_client import ScrapperClient
from src.server.telegram_client import TelegramClientManager
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='server.log',
)

logger = logging.getLogger(__name__)

class NewPropertyNotification(BaseModel):
    user_id: int
    # TODO

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    tg_client_manager = TelegramClientManager(
        session_name="fastapi_bot_session",
        api_id=int(os.getenv("BOT_API_ID")),
        api_hash=os.getenv("BOT_API_HASH"),
        bot_token=os.getenv("BOT_TOKEN"),
    )
    try:
        app.tg_client = tg_client_manager
        await tg_client_manager.__aenter__()
        yield
    finally:
        await tg_client_manager.__aexit__(None, None, None)

app = FastAPI(lifespan=lifespan)

async def get_telegram_client(app: FastAPI = Depends()) -> TelegramClientManager:
    return app.tg_client

@app.post("/new_property")
async def send_new_property_notification(
    new_property_notification: NewPropertyNotification,
):
    try:
        telegram_client = get_telegram_client()

        message = "TODO"

        await telegram_client.send_message(new_property_notification.user_id, message)
        logger.info(f"Sent notification to user {new_property_notification.user_id}")
        return {"status": "ok"}
    except Exception as e:
        logger.exception(f"Error sending message to user {new_property_notification.user_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)