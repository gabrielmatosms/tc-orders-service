from datetime import datetime
from typing import List, Optional

from pymongo.collection import Collection

from app.adapters.models.nosql.connection import order_item_collection
from app.domain.entities.order import OrderItem, OrderItemDb
from app.domain.interfaces.order_item_repository import OrderItemRepository


class NoSQLOrderItemRepository(OrderItemRepository):
    def __init__(self, collection: Collection = order_item_collection):
        self.collection = collection

    def get_by_order_id(self, order_id: int) -> List[OrderItemDb]:
        items = list(self.collection.find({"order_id": order_id}))
        return [self._map_to_entity(item) for item in items]

    def create(self, order_id: int, item: OrderItem) -> OrderItemDb:
        # Find the highest id to simulate auto-increment
        last_item = self.collection.find_one(sort=[("_id", -1)])
        next_id = 1 if not last_item else last_item["_id"] + 1
        
        now = datetime.utcnow()
        item_dict = {
            "_id": next_id,
            "order_id": order_id,
            "product_id": item.product_id,
            "quantity": item.quantity,
            "created_at": now,
            "updated_at": now
        }
        
        self.collection.insert_one(item_dict)
        return self._map_to_entity(item_dict)

    def create_many(self, order_id: int, items: List[OrderItem]) -> List[OrderItemDb]:
        # Find the highest id to simulate auto-increment
        last_item = self.collection.find_one(sort=[("_id", -1)])
        next_id = 1 if not last_item else last_item["_id"] + 1
        
        now = datetime.utcnow()
        item_dicts = []
        
        for i, item in enumerate(items):
            item_dict = {
                "_id": next_id + i,
                "order_id": order_id,
                "product_id": item.product_id,
                "quantity": item.quantity,
                "created_at": now,
                "updated_at": now
            }
            item_dicts.append(item_dict)
        
        if item_dicts:
            self.collection.insert_many(item_dicts)
        
        return [self._map_to_entity(item) for item in item_dicts]

    def delete(self, item_id: int) -> bool:
        result = self.collection.delete_one({"_id": item_id})
        return result.deleted_count > 0
    
    def _map_to_entity(self, data: dict) -> OrderItemDb:
        return OrderItemDb(
            id=data["_id"],
            order_id=data["order_id"],
            product_id=data["product_id"],
            quantity=data["quantity"],
            created_at=data["created_at"],
            updated_at=data["updated_at"]
        ) 