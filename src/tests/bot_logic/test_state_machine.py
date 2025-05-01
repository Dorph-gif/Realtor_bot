import pytest
from src.bot_logic.state_machine import get_state_machine

@pytest.fixture
def state_machine():
    sm = get_state_machine()
    sm.go_neutral(user_id=123)
    return sm

def test_goes_to_neutral(state_machine):
    user_id = 123
    state_machine.user_state[user_id] = "SOME_STATE"
    state_machine.user_property_filters[user_id] = {"city": "Москва"}
    state_machine.go_neutral(user_id)

    assert state_machine.user_state[user_id] == "NEUTRAL"
    assert state_machine.user_property_state[user_id] == 0
    assert state_machine.user_property_filters[user_id] == {}
    assert state_machine.user_update_param[user_id] == {}
    assert state_machine.user_creating_property_param[user_id] == 0

def test_get_state_initializes_neutral(state_machine):
    user_id = 999
    state = state_machine.get_state(user_id)
    assert state == "NEUTRAL"
    assert state_machine.user_property_state[user_id] == 0

def test_get_filter_param_type_valid(state_machine):
    assert state_machine.get_filter_param_type("city") == "str"
    assert state_machine.get_filter_param_type("MIN_PRICE") == "int"

def test_get_filter_param_type_invalid_raises(state_machine):
    with pytest.raises(ValueError):
        state_machine.get_filter_param_type("nonexistent")