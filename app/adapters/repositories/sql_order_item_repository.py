from typing import List, Optional

from sqlalchemy.orm import Session

from app.adapters.models.sql.order_item_model import OrderItemModel
from app.domain.entities.order import OrderItem, OrderItemDb
from app.domain.interfaces.order_item_repository import OrderItemRepository


class SQLOrderItemRepository(OrderItemRepository):
    def __init__(self, db_session: Session):
        self.db_session = db_session

    def get_by_order_id(self, order_id: int) -> List[OrderItemDb]:
        items = self.db_session.query(OrderItemModel).filter(OrderItemModel.order_id == order_id).all()
        return [self._map_to_entity(item) for item in items]

    def create(self, order_id: int, item: OrderItem) -> OrderItemDb:
        db_item = OrderItemModel(
            order_id=order_id,
            product_id=item.product_id,
            quantity=item.quantity
        )
        
        self.db_session.add(db_item)
        self.db_session.commit()
        self.db_session.refresh(db_item)
        
        return self._map_to_entity(db_item)

    def create_many(self, order_id: int, items: List[OrderItem]) -> List[OrderItemDb]:
        db_items = []
        
        for item in items:
            db_item = OrderItemModel(
                order_id=order_id,
                product_id=item.product_id,
                quantity=item.quantity
            )
            self.db_session.add(db_item)
            db_items.append(db_item)
        
        self.db_session.commit()
        
        # Refresh all items to get their generated IDs
        for item in db_items:
            self.db_session.refresh(item)
        
        return [self._map_to_entity(item) for item in db_items]

    def delete(self, item_id: int) -> bool:
        item = self.db_session.query(OrderItemModel).filter(OrderItemModel.id == item_id).first()
        if not item:
            return False
        
        self.db_session.delete(item)
        self.db_session.commit()
        return True
    
    def _map_to_entity(self, model: OrderItemModel) -> OrderItemDb:
        return OrderItemDb(
            id=model.id,
            order_id=model.order_id,
            product_id=model.product_id,
            quantity=model.quantity,
            created_at=model.created_at,
            updated_at=model.updated_at
        ) 