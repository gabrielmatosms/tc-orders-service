from sqlalchemy import Column, ForeignKey, Integer
from sqlalchemy.orm import relationship

from app.adapters.models.sql.base import BaseModel


class OrderItemModel(BaseModel):
    __tablename__ = "order_items"

    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    product_id = Column(Integer, nullable=False)
    quantity = Column(Integer, nullable=False)
    
    # Relationship with Order
    order = relationship("OrderModel", back_populates="items") 