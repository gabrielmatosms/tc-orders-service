import pytest
from unittest.mock import patch, AsyncMock
import httpx

from app.adapters.http.service_client import ServiceClient
from app.config import settings

@pytest.fixture
def service_client():
    return ServiceClient()

@pytest.mark.asyncio
async def test_get_customer_success(service_client):
    customer_data = {"id": 1, "name": "Test Customer"}
    mock_response = AsyncMock()
    mock_response.status_code = 200
    mock_response.json = AsyncMock(return_value=customer_data)
    
    with patch("httpx.AsyncClient.get", return_value=mock_response):
        result = await service_client.get_customer(1)
        assert result == customer_data

@pytest.mark.asyncio
async def test_get_customer_not_found(service_client):
    mock_response = AsyncMock()
    mock_response.status_code = 404
    
    with patch("httpx.AsyncClient.get", return_value=mock_response):
        result = await service_client.get_customer(999)
        assert result is None

@pytest.mark.asyncio
async def test_get_customer_request_error(service_client):
    mock_response = AsyncMock()
    mock_response.status_code = 500
    
    with patch("httpx.AsyncClient.get", return_value=mock_response):
        result = await service_client.get_customer(1)
        assert result is None

@pytest.mark.asyncio
async def test_get_product_success(service_client):
    product_data = {"id": 1, "name": "Test Product", "price": 10.99, "quantity": 5}
    mock_response = AsyncMock()
    mock_response.status_code = 200
    mock_response.json = AsyncMock(return_value=product_data)
    
    with patch("httpx.AsyncClient.get", return_value=mock_response):
        result = await service_client.get_product(1)
        assert result == product_data

@pytest.mark.asyncio
async def test_get_product_not_found(service_client):
    mock_response = AsyncMock()
    mock_response.status_code = 404
    
    with patch("httpx.AsyncClient.get", return_value=mock_response):
        result = await service_client.get_product(999)
        assert result is None

@pytest.mark.asyncio
async def test_get_product_request_error(service_client):
    mock_response = AsyncMock()
    mock_response.status_code = 500
    
    with patch("httpx.AsyncClient.get", return_value=mock_response):
        result = await service_client.get_product(1)
        assert result is None

@pytest.mark.asyncio
async def test_get_products_success(service_client):
    product_data_1 = {"id": 1, "name": "Product 1", "price": 10.99, "quantity": 5}
    product_data_2 = {"id": 2, "name": "Product 2", "price": 5.99, "quantity": 3}
    
    mock_response_1 = AsyncMock()
    mock_response_1.status_code = 200
    mock_response_1.json = AsyncMock(return_value=product_data_1)
    
    mock_response_2 = AsyncMock()
    mock_response_2.status_code = 200
    mock_response_2.json = AsyncMock(return_value=product_data_2)
    
    with patch("httpx.AsyncClient.get", side_effect=[mock_response_1, mock_response_2]):
        result = await service_client.get_products([1, 2])
        assert result == {1: product_data_1, 2: product_data_2}

@pytest.mark.asyncio
async def test_get_products_partial_success(service_client):
    product_data = {"id": 1, "name": "Product 1", "price": 10.99, "quantity": 5}
    
    mock_response_1 = AsyncMock()
    mock_response_1.status_code = 200
    mock_response_1.json = AsyncMock(return_value=product_data)
    
    mock_response_2 = AsyncMock()
    mock_response_2.status_code = 404
    
    with patch("httpx.AsyncClient.get", side_effect=[mock_response_1, mock_response_2]):
        result = await service_client.get_products([1, 2])
        assert result == {1: product_data}

@pytest.mark.asyncio
async def test_get_products_all_fail(service_client):
    mock_response_1 = AsyncMock()
    mock_response_1.status_code = 404
    
    mock_response_2 = AsyncMock()
    mock_response_2.status_code = 404
    
    with patch("httpx.AsyncClient.get", side_effect=[mock_response_1, mock_response_2]):
        result = await service_client.get_products([1, 2])
        assert result == {}

@pytest.mark.asyncio
async def test_update_product_quantity_success(service_client):
    mock_response = AsyncMock()
    mock_response.status_code = 200
    
    with patch("httpx.AsyncClient.patch", return_value=mock_response):
        result = await service_client.update_product_quantity(1, 5)
        assert result is True

@pytest.mark.asyncio
async def test_update_product_quantity_failure(service_client):
    mock_response = AsyncMock()
    mock_response.status_code = 400
    
    with patch("httpx.AsyncClient.patch", return_value=mock_response):
        result = await service_client.update_product_quantity(1, 5)
        assert result is False

@pytest.mark.asyncio
async def test_update_product_quantity_request_error(service_client):
    mock_response = AsyncMock()
    mock_response.status_code = 500
    
    with patch("httpx.AsyncClient.patch", return_value=mock_response):
        result = await service_client.update_product_quantity(1, 5)
        assert result is False

@pytest.mark.asyncio
async def test_notify_payment_service_success(service_client):
    payment_data = {"id": 1, "order_id": 1, "amount": 25.98, "status": "Pending"}
    mock_response = AsyncMock()
    mock_response.status_code = 201
    mock_response.json = AsyncMock(return_value=payment_data)
    
    with patch("httpx.AsyncClient.post", return_value=mock_response):
        result = await service_client.notify_payment_service(1, 25.98)
        assert result == payment_data

@pytest.mark.asyncio
async def test_notify_payment_service_failure(service_client):
    mock_response = AsyncMock()
    mock_response.status_code = 400
    
    with patch("httpx.AsyncClient.post", return_value=mock_response):
        result = await service_client.notify_payment_service(1, 25.98)
        assert result is None

@pytest.mark.asyncio
async def test_notify_payment_service_request_error(service_client):
    mock_response = AsyncMock()
    mock_response.status_code = 500
    
    with patch("httpx.AsyncClient.post", return_value=mock_response):
        result = await service_client.notify_payment_service(1, 25.98)
        assert result is None 