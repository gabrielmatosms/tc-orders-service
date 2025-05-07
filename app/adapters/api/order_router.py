from decimal import Decimal
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.adapters.http.service_client import ServiceClient
from app.adapters.models.sql.session import get_db
from app.adapters.repositories import RepositoryType, get_order_repository, get_order_item_repository
from app.application.use_cases.order_use_cases import OrderUseCases
from app.domain.entities.order import Order, OrderDb, OrderStatus, PaymentStatus

router = APIRouter()

# Helper function to get order use cases with SQL repositories
def get_order_use_cases(db: Session = Depends(get_db)) -> OrderUseCases:
    order_repository = get_order_repository(RepositoryType.SQL, db)
    order_item_repository = get_order_item_repository(RepositoryType.SQL, db)
    return OrderUseCases(order_repository, order_item_repository)


@router.get("/", response_model=List[OrderDb])
def get_all_orders(use_cases: OrderUseCases = Depends(get_order_use_cases)):
    return use_cases.get_all_orders()


@router.get("/{order_id}", response_model=OrderDb)
def get_order(order_id: int, use_cases: OrderUseCases = Depends(get_order_use_cases)):
    order = use_cases.get_order_by_id(order_id)
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Order with ID {order_id} not found"
        )
    return order


@router.get("/status/{status_name}", response_model=List[OrderDb])
def get_orders_by_status(
    status_name: OrderStatus, use_cases: OrderUseCases = Depends(get_order_use_cases)
):
    return use_cases.get_orders_by_status(status_name)


@router.post("/", response_model=OrderDb, status_code=status.HTTP_201_CREATED)
async def create_order(order: Order, use_cases: OrderUseCases = Depends(get_order_use_cases)):
    # Validate customer ID if provided
    if order.customer_id:
        service_client = ServiceClient()
        customer = await service_client.get_customer(order.customer_id)
        if not customer:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Customer with ID {order.customer_id} not found"
            )
    
    # Validate products and get their prices
    if not order.items:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Order must have at least one item"
        )
    
    service_client = ServiceClient()
    product_ids = [item.product_id for item in order.items]
    products = await service_client.get_products(product_ids)
    
    if len(products) != len(product_ids):
        missing_ids = set(product_ids) - set(products.keys())
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Products with IDs {missing_ids} not found"
        )
    
    # Check product quantities
    for item in order.items:
        product = products[item.product_id]
        if product["quantity"] < item.quantity:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Not enough stock for product {product['name']} (ID: {item.product_id})"
            )
    
    # Create price map for total calculation
    price_map = {
        product_id: Decimal(str(product["price"])) 
        for product_id, product in products.items()
    }
    
    # Create the order
    created_order = use_cases.create_order(order, price_map)
    
    # Update product quantities
    for item in order.items:
        await service_client.update_product_quantity(item.product_id, -item.quantity)
    
    # Notify payment service
    if created_order.total > 0:
        await service_client.notify_payment_service(created_order.id, float(created_order.total))
    
    return created_order


@router.patch("/{order_id}/status/{status_name}", response_model=OrderDb)
def update_order_status(
    order_id: int, 
    status_name: OrderStatus, 
    use_cases: OrderUseCases = Depends(get_order_use_cases)
):
    updated_order = use_cases.update_order_status(order_id, status_name)
    if not updated_order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Order with ID {order_id} not found"
        )
    return updated_order


@router.patch("/{order_id}/payment-status/{payment_status}", response_model=OrderDb)
def update_payment_status(
    order_id: int, 
    payment_status: PaymentStatus, 
    use_cases: OrderUseCases = Depends(get_order_use_cases)
):
    updated_order = use_cases.update_payment_status(order_id, payment_status)
    if not updated_order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Order with ID {order_id} not found"
        )
    return updated_order 