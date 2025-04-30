from telethon import TelegramClient
from telethon.events import NewMessage
from telethon import TelegramClient, events, Button

from src.bot_logic.utils import go_to_neutral_state

class StartCommandHandler:
    def __init__(self, client: TelegramClient):
        self.client = client

    async def execute(self, event):
        await go_to_neutral_state(event.chat_id, self.client)

    def register_handlers(self):
        self.client.add_event_handler(
            self.execute,
            events.NewMessage(pattern="/start"),
        )
        self.client.add_event_handler(
            self.execute,
            events.CallbackQuery(data="/start"),
        )