import pytest
from unittest.mock import MagicMock
from decimal import Decimal
from datetime import datetime

from app.application.use_cases.order_use_cases import OrderUseCases
from app.domain.entities.order import Order, OrderDb, OrderItem, OrderItemDb, OrderStatus, PaymentStatus
from app.domain.interfaces.order_repository import OrderRepository
from app.domain.interfaces.order_item_repository import OrderItemRepository


class TestOrderUseCases:
    def setup_method(self):
        self.mock_order_repo = MagicMock(spec=OrderRepository)
        self.mock_order_item_repo = MagicMock(spec=OrderItemRepository)
        
        self.use_cases = OrderUseCases(
            order_repository=self.mock_order_repo,
            order_item_repository=self.mock_order_item_repo
        )

    def test_get_all_orders(self):
        now = datetime.utcnow()
        orders = [
            OrderDb(
                id=1, customer_id=1, status=OrderStatus.PLACED,
                payment_status=PaymentStatus.PENDING, items=[],
                total=Decimal("25.98"), created_at=now, updated_at=now
            ),
            OrderDb(
                id=2, customer_id=2, status=OrderStatus.DELIVERED,
                payment_status=PaymentStatus.APPROVED, items=[],
                total=Decimal("15.99"), created_at=now, updated_at=now
            )
        ]
        self.mock_order_repo.get_all.return_value = orders

        result = self.use_cases.get_all_orders()

        assert len(result) == 2
        assert result[0].id == 1
        assert result[1].id == 2
        self.mock_order_repo.get_all.assert_called_once()

    def test_get_order_by_id(self):
        now = datetime.utcnow()
        order = OrderDb(
            id=1, customer_id=1, status=OrderStatus.PLACED,
            payment_status=PaymentStatus.PENDING, items=[],
            total=Decimal("25.98"), created_at=now, updated_at=now
        )
        self.mock_order_repo.get_by_id.return_value = order

        result = self.use_cases.get_order_by_id(1)

        assert result.id == 1
        assert result.status == OrderStatus.PLACED
        self.mock_order_repo.get_by_id.assert_called_once_with(1)
        
    def test_get_orders_by_status(self):
        now = datetime.utcnow()
        orders = [
            OrderDb(
                id=1, customer_id=1, status=OrderStatus.PLACED,
                payment_status=PaymentStatus.PENDING, items=[],
                total=Decimal("25.98"), created_at=now, updated_at=now
            ),
            OrderDb(
                id=3, customer_id=3, status=OrderStatus.PLACED,
                payment_status=PaymentStatus.PENDING, items=[],
                total=Decimal("35.97"), created_at=now, updated_at=now
            )
        ]
        self.mock_order_repo.get_by_status.return_value = orders

        result = self.use_cases.get_orders_by_status(OrderStatus.PLACED)

        assert len(result) == 2
        assert all(order.status == OrderStatus.PLACED for order in result)
        self.mock_order_repo.get_by_status.assert_called_once_with(OrderStatus.PLACED)
        
    def test_create_order_with_items(self):
        now = datetime.utcnow()
        order_items = [OrderItem(product_id=1, quantity=2), OrderItem(product_id=2, quantity=1)]
        order = Order(customer_id=1, items=order_items)
        
        created_order = OrderDb(
            id=1, customer_id=1, status=OrderStatus.PLACED, 
            payment_status=PaymentStatus.PENDING, items=[],
            total=Decimal("0"), created_at=now, updated_at=now
        )
        
        created_items = [
            OrderItemDb(
                id=1, order_id=1, product_id=1, quantity=2,
                created_at=now, updated_at=now
            ),
            OrderItemDb(
                id=2, order_id=1, product_id=2, quantity=1,
                created_at=now, updated_at=now
            )
        ]
        
        self.mock_order_repo.create.return_value = created_order
        self.mock_order_item_repo.create_many.return_value = created_items
        
        product_prices = {1: Decimal("10.99"), 2: Decimal("5.99")}
        
        result = self.use_cases.create_order(order, product_prices)
        
        self.mock_order_repo.create.assert_called_once_with(order)
        self.mock_order_item_repo.create_many.assert_called_once_with(1, order_items)
        self.mock_order_repo.update_total.assert_called_once()
        
    def test_update_order_status(self):
        now = datetime.utcnow()
        order_id = 1
        new_status = OrderStatus.CONFIRMED
        
        updated_order = OrderDb(
            id=order_id, customer_id=1, status=new_status,
            payment_status=PaymentStatus.PENDING, items=[],
            total=Decimal("25.98"), created_at=now, updated_at=now
        )
        
        self.mock_order_repo.update_status.return_value = updated_order
        
        result = self.use_cases.update_order_status(order_id, new_status)
        
        assert result.status == new_status
        self.mock_order_repo.update_status.assert_called_once_with(order_id, new_status)
        
    def test_update_payment_status(self):
        now = datetime.utcnow()
        order_id = 1
        new_payment_status = PaymentStatus.APPROVED
        
        existing_order = OrderDb(
            id=order_id, customer_id=1, status=OrderStatus.PLACED,
            payment_status=PaymentStatus.PENDING, items=[],
            total=Decimal("25.98"), created_at=now, updated_at=now
        )
        
        updated_order = OrderDb(
            id=order_id, customer_id=1, status=OrderStatus.CONFIRMED,
            payment_status=new_payment_status, items=[],
            total=Decimal("25.98"), created_at=now, updated_at=now
        )
        
        self.mock_order_repo.get_by_id.return_value = existing_order
        self.mock_order_repo.update_payment_status.return_value = updated_order
        self.mock_order_repo.update_status.return_value = updated_order
        
        result = self.use_cases.update_payment_status(order_id, new_payment_status)
        
        assert result.payment_status == new_payment_status
        self.mock_order_repo.update_status.assert_called_once_with(order_id, OrderStatus.CONFIRMED)
        self.mock_order_repo.update_payment_status.assert_called_once_with(order_id, new_payment_status)
        
    def test_add_item_to_order(self):
        now = datetime.utcnow()
        order_id = 1
        item = OrderItem(product_id=3, quantity=1)
        product_price = Decimal("7.99")
        
        existing_order = OrderDb(
            id=order_id, customer_id=1, status=OrderStatus.PLACED,
            payment_status=PaymentStatus.PENDING, items=[],
            total=Decimal("25.98"), created_at=now, updated_at=now
        )
        
        created_item = OrderItemDb(
            id=3, order_id=order_id, product_id=3, quantity=1,
            created_at=now, updated_at=now
        )
        
        updated_order = OrderDb(
            id=order_id, customer_id=1, status=OrderStatus.PLACED,
            payment_status=PaymentStatus.PENDING, 
            items=[created_item],
            total=Decimal("33.97"),
            created_at=now, updated_at=now
        )
        
        self.mock_order_repo.get_by_id.side_effect = [existing_order, updated_order]
        self.mock_order_item_repo.create.return_value = created_item
        
        result = self.use_cases.add_item_to_order(order_id, item, product_price)
        
        assert result.total == Decimal("33.97")
        self.mock_order_repo.get_by_id.assert_called_with(order_id)
        self.mock_order_item_repo.create.assert_called_once_with(order_id, item)
        self.mock_order_repo.update_total.assert_called_once()
        
    def test_add_item_to_non_placed_order(self):
        now = datetime.utcnow()
        order_id = 1
        item = OrderItem(product_id=3, quantity=1)
        product_price = Decimal("7.99")
        
        existing_order = OrderDb(
            id=order_id, customer_id=1, status=OrderStatus.CONFIRMED,
            payment_status=PaymentStatus.APPROVED, items=[],
            total=Decimal("25.98"), created_at=now, updated_at=now
        )
        
        self.mock_order_repo.get_by_id.return_value = existing_order
        
        with pytest.raises(ValueError, match="Cannot modify an order that is not in PLACED status"):
            self.use_cases.add_item_to_order(order_id, item, product_price)
        
        self.mock_order_repo.get_by_id.assert_called_once_with(order_id)
        self.mock_order_item_repo.create.assert_not_called()
        self.mock_order_repo.update_total.assert_not_called() 