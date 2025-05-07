from decimal import Decimal
from typing import List, Optional

from sqlalchemy.orm import Session

from app.adapters.models.sql.order_model import OrderModel
from app.domain.entities.order import Order, OrderDb, OrderStatus, PaymentStatus
from app.domain.interfaces.order_repository import OrderRepository


class SQLOrderRepository(OrderRepository):
    def __init__(self, db_session: Session):
        self.db_session = db_session

    def get_all(self) -> List[OrderDb]:
        orders = self.db_session.query(OrderModel).all()
        return [self._map_to_entity(order) for order in orders]

    def get_by_id(self, order_id: int) -> Optional[OrderDb]:
        order = self.db_session.query(OrderModel).filter(OrderModel.id == order_id).first()
        return self._map_to_entity(order) if order else None

    def get_by_status(self, status: OrderStatus) -> List[OrderDb]:
        orders = self.db_session.query(OrderModel).filter(OrderModel.status == status).all()
        return [self._map_to_entity(order) for order in orders]

    def create(self, order: Order) -> OrderDb:
        db_order = OrderModel(
            customer_id=order.customer_id,
            status=OrderStatus.PLACED,
            payment_status=PaymentStatus.PENDING,
            total=Decimal("0.00")  # Initial total, will be updated after items are added
        )
        self.db_session.add(db_order)
        self.db_session.commit()
        self.db_session.refresh(db_order)
        
        # Return order with empty items list since they'll be added separately
        return OrderDb(
            id=db_order.id,
            customer_id=db_order.customer_id,
            status=OrderStatus(db_order.status),
            payment_status=PaymentStatus(db_order.payment_status),
            items=[],
            total=db_order.total,
            created_at=db_order.created_at,
            updated_at=db_order.updated_at
        )

    def update_status(self, order_id: int, status: OrderStatus) -> Optional[OrderDb]:
        db_order = self.db_session.query(OrderModel).filter(OrderModel.id == order_id).first()
        if not db_order:
            return None
        
        db_order.status = status
        self.db_session.commit()
        self.db_session.refresh(db_order)
        return self._map_to_entity(db_order)

    def update_payment_status(self, order_id: int, payment_status: PaymentStatus) -> Optional[OrderDb]:
        db_order = self.db_session.query(OrderModel).filter(OrderModel.id == order_id).first()
        if not db_order:
            return None
        
        db_order.payment_status = payment_status
        self.db_session.commit()
        self.db_session.refresh(db_order)
        return self._map_to_entity(db_order)
    
    def update_total(self, order_id: int, total: Decimal) -> Optional[OrderDb]:
        db_order = self.db_session.query(OrderModel).filter(OrderModel.id == order_id).first()
        if not db_order:
            return None
        
        db_order.total = total
        self.db_session.commit()
        self.db_session.refresh(db_order)
        return self._map_to_entity(db_order)
    
    def _map_to_entity(self, model: OrderModel) -> OrderDb:
        return OrderDb(
            id=model.id,
            customer_id=model.customer_id,
            status=OrderStatus(model.status),
            payment_status=PaymentStatus(model.payment_status),
            items=model.items,  # This will already contain the loaded items due to relationship
            total=model.total,
            created_at=model.created_at,
            updated_at=model.updated_at
        ) 