from abc import ABC, abstractmethod
from typing import List, Optional

from app.domain.entities.order import OrderItem, OrderItemDb


class OrderItemRepository(ABC):
    @abstractmethod
    def get_by_order_id(self, order_id: int) -> List[OrderItemDb]:
        pass

    @abstractmethod
    def create(self, order_id: int, item: OrderItem) -> OrderItemDb:
        pass

    @abstractmethod
    def create_many(self, order_id: int, items: List[OrderItem]) -> List[OrderItemDb]:
        pass

    @abstractmethod
    def delete(self, item_id: int) -> bool:
        pass 