from enum import Enum
from typing import Optional

from sqlalchemy.orm import Session

from app.domain.interfaces.order_repository import OrderRepository
from app.domain.interfaces.order_item_repository import OrderItemRepository
from .sql_order_repository import SQLOrderRepository
from .nosql_order_repository import NoSQLOrderRepository
from .sql_order_item_repository import SQLOrderItemRepository
from .nosql_order_item_repository import NoSQLOrderItemRepository


class RepositoryType(str, Enum):
    SQL = "sql"
    NOSQL = "nosql"


def get_order_repository(
    repository_type: RepositoryType, db_session: Optional[Session] = None
) -> OrderRepository:
    if repository_type == RepositoryType.SQL:
        if not db_session:
            raise ValueError("DB session is required for SQL repository")
        return SQLOrderRepository(db_session)
    else:
        return NoSQLOrderRepository()


def get_order_item_repository(
    repository_type: RepositoryType, db_session: Optional[Session] = None
) -> OrderItemRepository:
    if repository_type == RepositoryType.SQL:
        if not db_session:
            raise ValueError("DB session is required for SQL repository")
        return SQLOrderItemRepository(db_session)
    else:
        return NoSQLOrderItemRepository()
