import pytest
from unittest.mock import patch, MagicMock
from src.bot_logic.database_service_client import DatabaseServiceClient

@pytest.fixture
def mock_client():
    """Fixture to create a mock instance of DatabaseServiceClient"""
    return DatabaseServiceClient(base_url="http://db_service:8005")
    
@pytest.mark.asyncio
@patch("requests.post")
async def test_new_property_filter(mock_post, mock_client):
    user_id = 123
    filter_data = {"min_price": 1000, "max_price": 5000, "city": "Moscow"}
    
    mock_response = MagicMock()
    mock_response.json.return_value = {"status": "success", "filter_id": 1}
    mock_post.return_value = mock_response
    
    response = await mock_client.new_property_filter(user_id, filter_data)
    
    mock_post.assert_called_once_with("http://db_service:8005/create_filter", json={
        "telegram_id": user_id,
        "min_price": 1000,
        "max_price": 5000,
        "city": "Moscow"
    })
    
    assert response == {"status": "success", "filter_id": 1}
    
@pytest.mark.asyncio
@patch("requests.post")
async def test_update_property_filter(mock_post, mock_client):
    user_id = 123
    filter_id = 1
    update_param = "max_price"
    new_value = "4000"
    param_type = "int"
    
    mock_response = MagicMock()
    mock_response.json.return_value = {"status": "success", "filter_id": filter_id}
    mock_post.return_value = mock_response
    
    response = await mock_client.update_property_filter(user_id, filter_id, update_param, new_value, param_type)
    
    mock_post.assert_called_once_with("http://db_service:8005/update_filter", json={
        "telegram_id": user_id,
        "filter_id": filter_id,
        "filter_param": update_param,
        "value": new_value,
        "type": param_type
    })
    
    assert response == {"status": "success", "filter_id": filter_id}
    
@pytest.mark.asyncio
@patch("requests.get")
async def test_get_property_filters_list(mock_get, mock_client):
    user_id = 123
    mock_response = MagicMock()
    mock_response.json.return_value = {"filters": [{"id": 1, "min_price": 1000, "max_price": 5000, "city": "Moscow"}]}
    mock_get.return_value = mock_response
    
    response = await mock_client.get_property_filters_list(user_id)
    
    mock_get.assert_called_once_with("http://db_service:8005/get_filters", params={"telegram_id": user_id})
    
    assert response == {"filters": [{"id": 1, "min_price": 1000, "max_price": 5000, "city": "Moscow"}]}
    
@pytest.mark.asyncio
@patch("requests.get")
async def test_get_property_filter(mock_get, mock_client):
    filter_id = 1
    mock_response = MagicMock()
    mock_response.json.return_value = {"id": 1, "min_price": 1000, "max_price": 5000, "city": "Moscow"}
    mock_get.return_value = mock_response
    
    response = await mock_client.get_property_filter(filter_id)
    
    mock_get.assert_called_once_with("http://db_service:8005/get_filter", params={"filter_id": filter_id})
    
    assert response == {"id": 1, "min_price": 1000, "max_price": 5000, "city": "Moscow"}
    
@pytest.mark.asyncio
@patch("requests.delete")
async def test_delete_property_filter(mock_delete, mock_client):
    user_id = 123
    filter_id = 1
    
    mock_response = MagicMock()
    mock_response.json.return_value = {"status": "success"}
    mock_delete.return_value = mock_response
    
    response = await mock_client.delete_property_filter(user_id, filter_id)
    
    mock_delete.assert_called_once_with("http://db_service:8005/delete_filter", params={"telegram_id": user_id, "filter_id": filter_id})
    
    assert response == {"status": "success"}
    