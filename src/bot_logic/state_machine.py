import logging
import os

from src.bot_logic.messages import MESSAGES

LOG_FILE = os.path.join("logs", "state_machine.log")

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename=LOG_FILE,
)
logger = logging.getLogger(__name__)

property_states = [
    "NEUTRAL", "NAME", "PROPERTY_TYPE", "DEAL_TYPE", "CITY", "AREAS", "MIN_PRICE",
    "MAX_PRICE", "MIN_ROOMS", "MAX_ROOMS", "MIN_TOTAL_AREA", "MAX_TOTAL_AREA", "BALCONY",
    "RENOVATED", "MIN_DEPOSIT", "MAX_DEPOSIT", "FLOOR", "IS_ACTIVE", "TOTAL_FLOORS", "CONFIRMATION"
]

property_state_type = {
    "NEUTRAL":"str", "NAME":"str", "PROPERTY_TYPE":"str", "DEAL_TYPE":"str", "CITY":"str", "AREAS":"list", "MIN_PRICE":"int",
    "MAX_PRICE":"int", "MIN_ROOMS":"int", "MAX_ROOMS":"int", "MIN_TOTAL_AREA":"int", "MAX_TOTAL_AREA":"int", "BALCONY":"bool",
    "RENOVATED":"str", "MIN_DEPOSIT":"int", "MAX_DEPOSIT":"int", "FLOOR":"int", "IS_ACTIVE":"bool", "TOTAL_FLOORS":"int", "CONFIRMATION":"bool"
}

add_property_states = [
    "RETURN_CONTACT", "PROPERTY_TYPE", "DEAL_TYPE", "PRICE", "CITY", "AREAS", "STREET", "HOUSE_NUMBER",
    "APARTMENT_NUMBER", "ROOMS", "BALCONY", "RENOVATED", "TOTAL_AREA", "FLOOR", "TOTAL_FLOORS", "DEPOSIT", "DESCRIPTION",
    "CONFIRMATION"
]

user_searching_states = [
    "NEUTRAL", "PROPERTY_FILTERS", "UPDATING", "CREATING_PROPERTY"
]

class StateMachine:
    def __init__(self):
        self.user_state = {}
        self.user_property_state = {}
        self.user_property_filters = {}
        self.user_update_param = {}
        self.user_creating_property_param = {}

    # ----------------- Common methods -----------------

    def go_neutral(self, user_id):
        logger.info(f"User {user_id}: перешли в состояние NEUTRAL")
        self.user_state[user_id] = "NEUTRAL"
        self.user_property_state[user_id] = 0
        self.user_property_filters[user_id] = {}
        self.user_update_param[user_id] = {}
        self.user_creating_property_param[user_id] = 0

    def get_state(self, user_id):
        if not user_id in self.user_state:
            self.go_neutral(user_id)
        return self.user_state[user_id]
    
    def get_filter_param_type(self, param_name: str):
        param_name = param_name.upper()
        if param_name not in property_state_type:
            raise ValueError("Wrong param name")
        return property_state_type[param_name]
    
    # ----------------- Update filter methods -----------------

    def start_updating(self, user_id):
        logger.info(f"User {user_id}: начали обновление фильтров")
        self.go_neutral(user_id)
        self.user_state[user_id] = "UPDATING"

    def start_update(self, user_id, filter_id):
        self.user_state[user_id] = "UPDATING"
        self.user_update_param[user_id] = [ "", filter_id ]

    def set_update_param(self, user_id, param_name):
        self.user_state[user_id] = "UPDATING"
        self.user_update_param[user_id][0] = param_name

    def get_user_update_param(self, user_id):
        if self.get_state(user_id) != "UPDATING":
            return [ "NEUTRAL", "NEUTRAL" ]
        return self.user_update_param[user_id][0]

    def get_user_update_filter(self, user_id):
        if self.user_state[user_id] != "UPDATING":
            logger.error(f"User {user_id}: попытка получить фильтр обновления вне процесса обновления")
            raise ValueError("Trying to get update filter out of update process")
        return int(self.user_update_param[user_id][1])
    
    def is_update_state_num(self, user_id):
        return (property_state_type[self.get_user_update_param(user_id)] == 'int')
    
    def is_update_state_list(self, user_id):
        return (property_state_type[self.get_user_update_param(user_id)] == 'list')
    
    def is_update_state_bool(self, user_id):
        return (property_state_type[self.get_user_update_param(user_id)] == 'list')

    def end_update(self, user_id):
        self.go_neutral(user_id)

    # ----------------- Create filter methods -----------------

    def starting_property_filter(self, user_id):
        logger.info(f"User {user_id}: начали ввод фильтров")
        self.user_state[user_id] = "PROPERTY_FILTERS"
        self.user_property_state[user_id] = 1

    def save_filter_info(self, user_id, filter_name: str, value):
        if not filter_name in property_states:
            logger.error(f"User {user_id}: попытка сохранить неверный фильтр {filter_name}")
            raise ValueError("Wrong filter name")
        self.user_property_filters[user_id][filter_name.lower()] = value
        logger.info(f"User {user_id}: сохранен фильтр {filter_name.lower()} = {value}")

    def next_property_filter(self, user_id):
        if self.user_property_state[user_id] == len(property_states) - 1:
            logger.error(f"User {user_id}: попытка перейти в следующее состояние после CONFIRMATION")
            self.go_neutral(user_id)
            raise ValueError("Trying to go to next state after CONFIRMATION state")
        self.user_property_state[user_id] += 1

    def get_property_state(self, user_id):
        if not user_id in self.user_property_state:
            self.user_property_state[user_id] = 0
        return property_states[self.user_property_state[user_id]]

    def is_state_num(self, user_id):
        if not user_id in self.user_property_state:
            self.user_property_state[user_id] = 0
        return (property_state_type[self.get_property_state(user_id)] == 'int')

    def is_state_list(self, user_id):
        if not user_id in self.user_property_state:
            self.user_property_state[user_id] = 0
        return (property_state_type[self.get_property_state(user_id)] == 'list')

    def is_state_bool(self, user_id):
        if not user_id in self.user_property_state:
            self.user_property_state[user_id] = 0
        return (property_state_type[self.get_property_state(user_id)] == 'bool')

    def get_property_filter(self, user_id):
        if self.get_property_state(user_id) != "CONFIRMATION":
            logger.error(f"User {user_id}: попытка получить фильтры до завершения ввода")
            raise ValueError("Trying to get filter info until complete")
        return self.user_property_filters[user_id]

    def is_valid_transition(self, user_id, expected_state):
        current_state = property_states[self.user_property_state.get(user_id)]
        logger.info(f"For user {user_id}: real_state: {current_state}, handler_state: {expected_state}")
        return current_state == expected_state

    # ----------------- New property methods -----------------

    def starting_add_property(self, user_id):
        logger.info(f"User {user_id}: начали ввод нового объекта")
        self.user_state[user_id] = "CREATING_PROPERTY"
        self.user_creating_property_param[user_id] = 0

    def next_creating_property_pram(self, user_id):
        self.user_creating_property_param[user_id] += 1

    def get_creating_property_param(self, user_id):
        logger.info(f"User {user_id}: получение параметра {self.user_creating_property_param[user_id]}")
        return add_property_states[self.user_creating_property_param[user_id]]
    
    async def send_creating_property_message(self, client, user_id):
        key = "CREATING_PROPERTY:"+self.get_creating_property_param(user_id)
        if self.user_creating_property_param[user_id] >= len(add_property_states):
            logger.error(f"User {user_id}: попытка перейти в следующее состояние после CONFIRMATION")
            self.go_neutral(user_id)
            raise ValueError("Trying to go to next state after CONFIRMATION state")
        logger.info(f"отправка сообщения key: {key}")
        message, buttons, name, type = MESSAGES[key]
        await client.send_message(user_id, message, buttons=buttons)

    def get_cur_param_name_type(self, user_id):
        key = "CREATING_PROPERTY:"+self.get_creating_property_param(user_id)
        if self.user_creating_property_param[user_id] >= len(add_property_states):
            logger.error(f"User {user_id}: попытка перейти в следующее состояние после CONFIRMATION")
            self.go_neutral(user_id)
            raise ValueError("Trying to go to next state after CONFIRMATION state")
        logger.info(f"отправка сообщения key: {key}")
        message, buttons, name, type = MESSAGES[key]
        return name, type    
        
    def end_creating_property(self, user_id):
        self.go_neutral(user_id)

global_state_machine = StateMachine()

def get_state_machine():
    return global_state_machine