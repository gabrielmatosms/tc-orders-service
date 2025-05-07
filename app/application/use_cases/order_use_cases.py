from decimal import Decimal
from typing import Dict, List, Optional

from app.domain.entities.order import Order, OrderDb, OrderItem, OrderStatus, PaymentStatus
from app.domain.interfaces.order_repository import OrderRepository
from app.domain.interfaces.order_item_repository import OrderItemRepository


class OrderUseCases:
    def __init__(
        self, 
        order_repository: OrderRepository,
        order_item_repository: OrderItemRepository
    ):
        self.order_repository = order_repository
        self.order_item_repository = order_item_repository

    def get_all_orders(self) -> List[OrderDb]:
        return self.order_repository.get_all()

    def get_order_by_id(self, order_id: int) -> Optional[OrderDb]:
        return self.order_repository.get_by_id(order_id)

    def get_orders_by_status(self, status: OrderStatus) -> List[OrderDb]:
        return self.order_repository.get_by_status(status)

    def create_order(self, order: Order, product_prices: Dict[int, Decimal] = None) -> OrderDb:
        """
        Create a new order with items.
        If product_prices is provided, it will be used to calculate the order total.
        """
        created_order = self.order_repository.create(order)
        
        # Add items to the order
        if order.items:
            created_items = self.order_item_repository.create_many(created_order.id, order.items)
            
            # Update the created order with the items
            created_order.items = created_items
            
            # Calculate and update the total if product prices are provided
            if product_prices:
                total = Decimal("0")
                for item in created_items:
                    if item.product_id in product_prices:
                        item_price = product_prices[item.product_id] * item.quantity
                        total += item_price
                
                # Update the order with the calculated total
                updated_order = self.order_repository.update_total(created_order.id, total)
                if updated_order:
                    created_order.total = total
        
        return created_order

    def update_order_status(self, order_id: int, status: OrderStatus) -> Optional[OrderDb]:
        return self.order_repository.update_status(order_id, status)

    def update_payment_status(self, order_id: int, payment_status: PaymentStatus) -> Optional[OrderDb]:
        order = self.order_repository.get_by_id(order_id)
        if not order:
            return None
            
        # If payment is approved and order is in PLACED status, change to CONFIRMED
        if payment_status == PaymentStatus.APPROVED and order.status == OrderStatus.PLACED:
            self.order_repository.update_status(order_id, OrderStatus.CONFIRMED)
            
        # Update payment status
        return self.order_repository.update_payment_status(order_id, payment_status)
    
    def add_item_to_order(self, order_id: int, item: OrderItem, product_price: Optional[Decimal] = None) -> Optional[OrderDb]:
        """Add an item to an existing order and optionally update the total"""
        order = self.order_repository.get_by_id(order_id)
        if not order:
            return None
            
        # Check if order can be modified (only in PLACED status)
        if order.status != OrderStatus.PLACED:
            raise ValueError("Cannot modify an order that is not in PLACED status")
            
        # Add the item
        created_item = self.order_item_repository.create(order_id, item)
        
        # Update the total if price is provided
        if product_price is not None:
            new_total = order.total + (product_price * Decimal(str(item.quantity)))
            self.order_repository.update_total(order_id, new_total)
            
        # Return the updated order
        return self.get_order_by_id(order_id) 