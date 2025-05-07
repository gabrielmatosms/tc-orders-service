from sqlalchemy import Column, ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import relationship

from app.adapters.models.sql.base import BaseModel


class OrderModel(BaseModel):
    __tablename__ = "orders"

    customer_id = Column(Integer, nullable=True)
    status = Column(String, nullable=False)
    payment_status = Column(String, nullable=False)
    total = Column(Numeric(precision=10, scale=2), nullable=False, default=0)
    
    # Relationship with OrderItems
    items = relationship("OrderItemModel", back_populates="order", cascade="all, delete-orphan") 