from typing import Any, Dict, List, Optional

import httpx

from app.config import settings
from app.domain.entities.order import Order, OrderItem


class ServiceClient:
    def __init__(self):
        self.customers_url = settings.CUSTOMERS_SERVICE_URL
        self.products_url = settings.PRODUCTS_SERVICE_URL
        self.payments_url = settings.PAYMENTS_SERVICE_URL
    
    async def get_customer(self, customer_id: int) -> Optional[Dict[str, Any]]:
        """Get customer information from the customers service"""
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(f"{self.customers_url}/api/v1/customers/{customer_id}")
                if response.status_code == 200:
                    return await response.json()
                return None
            except httpx.RequestError:
                return None
    
    async def get_product(self, product_id: int) -> Optional[Dict[str, Any]]:
        """Get product information from the products service"""
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(f"{self.products_url}/api/v1/products/{product_id}")
                if response.status_code == 200:
                    return await response.json()
                return None
            except httpx.RequestError:
                return None
    
    async def get_products(self, product_ids: List[int]) -> Dict[int, Dict[str, Any]]:
        """Get multiple products information from the products service"""
        result = {}
        async with httpx.AsyncClient() as client:
            for product_id in product_ids:
                try:
                    response = await client.get(f"{self.products_url}/api/v1/products/{product_id}")
                    if response.status_code == 200:
                        result[product_id] = await response.json()
                except httpx.RequestError:
                    continue
        return result
    
    async def update_product_quantity(self, product_id: int, quantity_change: int) -> bool:
        """Update product quantity in the products service"""
        async with httpx.AsyncClient() as client:
            try:
                response = await client.patch(
                    f"{self.products_url}/api/v1/products/{product_id}/quantity/{quantity_change}"
                )
                return response.status_code == 200
            except httpx.RequestError:
                return False
    
    async def notify_payment_service(self, order_id: int, total: float) -> Optional[Dict[str, Any]]:
        """Notify the payment service about a new order"""
        async with httpx.AsyncClient() as client:
            try:
                payment_data = {
                    "order_id": order_id,
                    "amount": total,
                    "status": "Pending"
                }
                response = await client.post(f"{self.payments_url}/api/v1/payments/", json=payment_data)
                if response.status_code in (200, 201):
                    return await response.json()
                return None
            except httpx.RequestError:
                return None 