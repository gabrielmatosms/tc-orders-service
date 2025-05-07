from pymongo import MongoClient

from app.config import settings

mongo_client = MongoClient(
    host=settings.NOSQL_HOST,
    port=settings.NOSQL_PORT,
)

db = mongo_client[settings.NOSQL_DB]

order_collection = db["orders"]
order_item_collection = db["order_items"] 