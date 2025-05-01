from typing import List, Optional

import logging
import os
from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
import uvicorn
import asyncio
from src.bot_logic.telegram_client import TelegramClientManager
from src.bot_logic.utils import send_property_info
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from dotenv import load_dotenv
from telethon import Button

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='server.log',
)

logger = logging.getLogger(__name__)

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

@app.post("/new_property_notification/{user_id}/{property_id}")
async def send_new_property_notification(
    user_id: int,
    property_id: int
):
    try:
        telegram_client = get_telegram_client()

        message = "Посмотрите на новое объявление, подъодящее под ваши фильтры!"
        buttons = [ 
            [Button.inline("Связаться с риелтором 🤝", f"like:-:{property_id}")],
            [Button.inline("В избранное ❤️", f"to_favorites:{property_id}")],
            [Button.inline("В меню", "/start")]
        ]
        await send_property_info(telegram_client, user_id, property_id, message="", buttons=buttons)

        await telegram_client.send_message(user_id, message, buttons=buttons)
        logger.info(f"Sent notification to user {user_id}")
        return {"status": "ok"}
    except Exception as e:
        logger.exception(f"Error sending message to user {user_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)