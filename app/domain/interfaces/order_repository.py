from abc import ABC, abstractmethod
from typing import List, Optional

from app.domain.entities.order import Order, OrderDb, OrderStatus, PaymentStatus


class OrderRepository(ABC):
    @abstractmethod
    def get_all(self) -> List[OrderDb]:
        pass

    @abstractmethod
    def get_by_id(self, order_id: int) -> Optional[OrderDb]:
        pass

    @abstractmethod
    def get_by_status(self, status: OrderStatus) -> List[OrderDb]:
        pass

    @abstractmethod
    def create(self, order: Order) -> OrderDb:
        pass

    @abstractmethod
    def update_status(self, order_id: int, status: OrderStatus) -> Optional[OrderDb]:
        pass

    @abstractmethod
    def update_payment_status(self, order_id: int, payment_status: PaymentStatus) -> Optional[OrderDb]:
        pass 