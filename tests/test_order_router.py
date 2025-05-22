import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi import FastAPI
from fastapi.testclient import TestClient
from decimal import Decimal
from datetime import datetime

from app.adapters.api.order_router import router, get_order_use_cases
from app.domain.entities.order import Order, OrderDb, OrderItem, OrderStatus, PaymentStatus
from app.adapters.repositories import RepositoryType

# Helper to override dependencies
class UseCasesOverride:
    def __init__(self, order_repo, order_item_repo):
        self.order_repo = order_repo
        self.order_item_repo = order_item_repo
    def __call__(self):
        from app.application.use_cases.order_use_cases import OrderUseCases
        return OrderUseCases(self.order_repo, self.order_item_repo)

@pytest.fixture
def mock_order_repo():
    return MagicMock()

@pytest.fixture
def mock_order_item_repo():
    return MagicMock()

@pytest.fixture
def mock_service_client():
    with patch("app.adapters.api.order_router.ServiceClient") as mock:
        client = mock.return_value
        client.get_customer = AsyncMock()
        client.get_products = AsyncMock()
        client.update_product_quantity = AsyncMock()
        client.notify_payment_service = AsyncMock()
        yield client

@pytest.fixture
def app_with_overrides(mock_order_repo, mock_order_item_repo):
    app = FastAPI()
    app.include_router(router, prefix="/orders", tags=["orders"])
    app.dependency_overrides[get_order_use_cases] = UseCasesOverride(mock_order_repo, mock_order_item_repo)
    return app

@pytest.fixture
def client(app_with_overrides):
    return TestClient(app_with_overrides)

def test_get_all_orders(client, mock_order_repo):
    now = datetime.now().isoformat()
    orders = [
        OrderDb(
            id=1, customer_id=1, status=OrderStatus.PLACED,
            payment_status=PaymentStatus.PENDING, items=[],
            total=Decimal("25.98"), created_at=now, updated_at=now
        )
    ]
    mock_order_repo.get_all.return_value = orders
    response = client.get("/orders/")
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["id"] == 1

def test_get_order_by_id(client, mock_order_repo):
    now = datetime.now().isoformat()
    order = OrderDb(
        id=1, customer_id=1, status=OrderStatus.PLACED,
        payment_status=PaymentStatus.PENDING, items=[],
        total=Decimal("25.98"), created_at=now, updated_at=now
    )
    mock_order_repo.get_by_id.return_value = order
    response = client.get("/orders/1")
    assert response.status_code == 200
    assert response.json()["id"] == 1

def test_get_order_by_id_not_found(client, mock_order_repo):
    mock_order_repo.get_by_id.return_value = None
    response = client.get("/orders/999")
    assert response.status_code == 404
    assert "Order with ID 999 not found" in response.json()["detail"]

def test_get_orders_by_status(client, mock_order_repo):
    now = datetime.now().isoformat()
    orders = [
        OrderDb(
            id=1, customer_id=1, status=OrderStatus.PLACED,
            payment_status=PaymentStatus.PENDING, items=[],
            total=Decimal("25.98"), created_at=now, updated_at=now
        )
    ]
    mock_order_repo.get_by_status.return_value = orders
    response = client.get(f"/orders/status/{OrderStatus.PLACED.value}")
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["id"] == 1

@pytest.mark.asyncio
async def test_create_order_success(client, mock_order_repo, mock_service_client):
    now = datetime.now().isoformat()
    mock_service_client.get_customer.return_value = {"id": 1, "name": "Test Customer"}
    mock_service_client.get_products.return_value = {
        1: {"id": 1, "name": "Product 1", "price": 10.99, "quantity": 5},
        2: {"id": 2, "name": "Product 2", "price": 5.99, "quantity": 3}
    }
    created_order = OrderDb(
        id=1, customer_id=1, status=OrderStatus.PLACED,
        payment_status=PaymentStatus.PENDING, items=[],
        total=Decimal("27.97"), created_at=now, updated_at=now
    )
    with patch("app.adapters.api.order_router.OrderUseCases.create_order", return_value=created_order):
        order_data = {
            "customer_id": 1,
            "items": [
                {"product_id": 1, "quantity": 2},
                {"product_id": 2, "quantity": 1}
            ]
        }
        response = client.post("/orders/", json=order_data)
        assert response.status_code == 201
        assert response.json()["id"] == 1
        assert response.json()["total"] == "27.97"
        mock_service_client.get_customer.assert_called_once_with(1)
        mock_service_client.get_products.assert_called_once_with([1, 2])
        mock_service_client.update_product_quantity.assert_any_call(1, -2)
        mock_service_client.update_product_quantity.assert_any_call(2, -1)
        mock_service_client.notify_payment_service.assert_called_once_with(1, 27.97)

@pytest.mark.asyncio
async def test_create_order_customer_not_found(client, mock_service_client):
    mock_service_client.get_customer.return_value = None
    order_data = {
        "customer_id": 999,
        "items": [{"product_id": 1, "quantity": 1}]
    }
    response = client.post("/orders/", json=order_data)
    assert response.status_code == 400
    assert "Customer with ID 999 not found" in response.json()["detail"]

@pytest.mark.asyncio
async def test_create_order_product_not_found(client, mock_service_client):
    mock_service_client.get_customer.return_value = {"id": 1, "name": "Test Customer"}
    mock_service_client.get_products.return_value = {}
    order_data = {
        "customer_id": 1,
        "items": [
            {"product_id": 999, "quantity": 1}
        ]
    }
    response = client.post("/orders/", json=order_data)
    assert response.status_code == 400
    assert "Products with IDs {999} not found" in response.json()["detail"]

@pytest.mark.asyncio
async def test_create_order_insufficient_stock(client, mock_service_client):
    mock_service_client.get_customer.return_value = {"id": 1, "name": "Test Customer"}
    mock_service_client.get_products.return_value = {
        1: {"id": 1, "name": "Product 1", "price": 10.99, "quantity": 1}
    }
    order_data = {
        "customer_id": 1,
        "items": [{"product_id": 1, "quantity": 2}]
    }
    response = client.post("/orders/", json=order_data)
    assert response.status_code == 400
    assert "Not enough stock for product Product 1 (ID: 1)" in response.json()["detail"]

def test_update_order_status(client, mock_order_repo):
    now = datetime.now().isoformat()
    updated_order = OrderDb(
        id=1, customer_id=1, status=OrderStatus.CONFIRMED,
        payment_status=PaymentStatus.PENDING, items=[],
        total=Decimal("25.98"), created_at=now, updated_at=now
    )
    mock_order_repo.update_status.return_value = updated_order
    response = client.patch(f"/orders/1/status/{OrderStatus.CONFIRMED.value}")
    assert response.status_code == 200
    assert response.json()["status"] == OrderStatus.CONFIRMED.value

def test_update_order_status_not_found(client, mock_order_repo):
    mock_order_repo.update_status.return_value = None
    response = client.patch(f"/orders/999/status/{OrderStatus.CONFIRMED.value}")
    assert response.status_code == 404
    assert "Order with ID 999 not found" in response.json()["detail"]

def test_update_payment_status(client, mock_order_repo):
    now = datetime.now().isoformat()
    updated_order = OrderDb(
        id=1, customer_id=1, status=OrderStatus.CONFIRMED,
        payment_status=PaymentStatus.APPROVED, items=[],
        total=Decimal("25.98"), created_at=now, updated_at=now
    )
    mock_order_repo.update_payment_status.return_value = updated_order
    response = client.patch(f"/orders/1/payment-status/{PaymentStatus.APPROVED.value}")
    assert response.status_code == 200
    assert response.json()["payment_status"] == PaymentStatus.APPROVED.value

def test_update_payment_status_not_found(client, mock_order_repo):
    mock_order_repo.update_payment_status.return_value = None
    response = client.patch(f"/orders/999/payment-status/{PaymentStatus.APPROVED.value}")
    assert response.status_code == 404
    assert "Order with ID 999 not found" in response.json()["detail"] 