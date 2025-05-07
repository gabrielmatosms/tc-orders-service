from datetime import datetime
from decimal import Decimal
from typing import List, Optional

from pymongo.collection import Collection

from app.adapters.models.nosql.connection import order_collection, order_item_collection
from app.domain.entities.order import Order, OrderDb, OrderItemDb, OrderStatus, PaymentStatus
from app.domain.interfaces.order_repository import OrderRepository


class NoSQLOrderRepository(OrderRepository):
    def __init__(self, collection: Collection = order_collection):
        self.collection = collection
        self.item_collection = order_item_collection

    def get_all(self) -> List[OrderDb]:
        orders = list(self.collection.find())
        return [self._map_to_entity(order) for order in orders]

    def get_by_id(self, order_id: int) -> Optional[OrderDb]:
        order = self.collection.find_one({"_id": order_id})
        return self._map_to_entity(order) if order else None

    def get_by_status(self, status: OrderStatus) -> List[OrderDb]:
        orders = list(self.collection.find({"status": status}))
        return [self._map_to_entity(order) for order in orders]

    def create(self, order: Order) -> OrderDb:
        # Find the highest id to simulate auto-increment
        last_order = self.collection.find_one(sort=[("_id", -1)])
        next_id = 1 if not last_order else last_order["_id"] + 1
        
        now = datetime.utcnow()
        order_dict = {
            "_id": next_id,
            "customer_id": order.customer_id,
            "status": OrderStatus.PLACED,
            "payment_status": PaymentStatus.PENDING,
            "total": 0,
            "created_at": now,
            "updated_at": now
        }
        
        self.collection.insert_one(order_dict)
        
        # Return order with empty items list since they'll be added separately
        return OrderDb(
            id=next_id,
            customer_id=order.customer_id,
            status=OrderStatus.PLACED,
            payment_status=PaymentStatus.PENDING,
            items=[],
            total=Decimal("0"),
            created_at=now,
            updated_at=now
        )

    def update_status(self, order_id: int, status: OrderStatus) -> Optional[OrderDb]:
        now = datetime.utcnow()
        result = self.collection.update_one(
            {"_id": order_id},
            {"$set": {"status": status, "updated_at": now}}
        )
        
        if result.modified_count == 0:
            return None
            
        return self.get_by_id(order_id)

    def update_payment_status(self, order_id: int, payment_status: PaymentStatus) -> Optional[OrderDb]:
        now = datetime.utcnow()
        result = self.collection.update_one(
            {"_id": order_id},
            {"$set": {"payment_status": payment_status, "updated_at": now}}
        )
        
        if result.modified_count == 0:
            return None
            
        return self.get_by_id(order_id)
    
    def update_total(self, order_id: int, total: Decimal) -> Optional[OrderDb]:
        now = datetime.utcnow()
        result = self.collection.update_one(
            {"_id": order_id},
            {"$set": {"total": float(total), "updated_at": now}}
        )
        
        if result.modified_count == 0:
            return None
            
        return self.get_by_id(order_id)
    
    def _map_to_entity(self, data: dict) -> OrderDb:
        # Get all items for this order
        items_data = list(self.item_collection.find({"order_id": data["_id"]}))
        items = [
            OrderItemDb(
                id=item["_id"],
                order_id=item["order_id"],
                product_id=item["product_id"],
                quantity=item["quantity"],
                created_at=item["created_at"],
                updated_at=item["updated_at"]
            )
            for item in items_data
        ]
        
        return OrderDb(
            id=data["_id"],
            customer_id=data.get("customer_id"),
            status=OrderStatus(data["status"]),
            payment_status=PaymentStatus(data["payment_status"]),
            items=items,
            total=Decimal(str(data["total"])),
            created_at=data["created_at"],
            updated_at=data["updated_at"]
        ) 