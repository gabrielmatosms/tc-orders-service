from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel


class OrderStatus(str, Enum):
    PLACED = "Order placed"
    CONFIRMED = "Order confirmed"
    PREPARING = "Preparing"
    READY_FOR_PICKUP = "Ready for pickup"
    OUT_FOR_DELIVERY = "Out for delivery"
    DELIVERED = "Delivered"
    CANCELED = "Canceled"
    REFUNDED = "Refunded"
    FINALIZED = "Finalized"


class PaymentStatus(str, Enum):
    PENDING = "Pending"
    APPROVED = "Approved"
    DENIED = "Denied"
    REJECTED = "Rejected"
    UNKNOWN = "Unknown"


class OrderItem(BaseModel):
    product_id: int
    quantity: int


class OrderItemDb(OrderItem):
    id: int
    order_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class Order(BaseModel):
    customer_id: Optional[int] = None
    items: List[OrderItem]


class OrderDb(Order):
    id: int
    status: OrderStatus
    payment_status: PaymentStatus
    created_at: datetime
    updated_at: datetime
    items: List[OrderItemDb]
    total: Decimal

    class Config:
        from_attributes = True 