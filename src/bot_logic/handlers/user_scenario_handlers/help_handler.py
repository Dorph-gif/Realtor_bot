from telethon import TelegramClient
from telethon.events import NewMessage
from telethon import TelegramClient, events, Button
from src.bot_logic.utils import go_to_neutral_state
import re

class HelpCommandHandler:
    def __init__(self, client: TelegramClient):
        self.client = client

    async def execute(self, event):
        instruction = "\
            Привет! Я бот риелтор, вот описание моих возможностей:\n\
            Для использования создайте фильтры, по которым хотите искать объекты недвижимости!\n\
            Кнопка `Новый фильтр` создает фильтр, чтобы получать уведомления о новых объектах по этому фильтру \
            выберите соответствующий параметр при создании.\n\
            Кнопка `Мои фильтры` выдаст список ваших фильтров.\n\
            Кнопка `Изменить фильтр` дает информацию о фильтре и позволяет его менять.\n\
            Кнопка `Смотреть объявления` запускает просмотр по определеному фильтру.\n\
            Кнопка `Удалить фильтр` удаляет фильтр.\
        "
        await self.client.send_message(event.chat_id, instruction)
        await go_to_neutral_state(event.chat_id, self.client)

    def register_handlers(self):
        self.client.add_event_handler(
            self.execute,
            events.NewMessage(pattern="/help"),
        )
        self.client.add_event_handler(
            self.execute,
            events.CallbackQuery(data="/help"),
        )