from __future__ import annotations

from pymongo import MongoClient, UpdateOne

from src.config import settings
from src.models import CatalogItem


def load_to_mongodb(items: list[CatalogItem]) -> int:
    if not items:
        return 0

    client = MongoClient(settings.mongo_uri)
    collection = client[settings.mongo_database][settings.mongo_collection]

    operations = [
        UpdateOne(
            {"external_id": item.external_id},
            {"$set": item.to_dict()},
            upsert=True,
        )
        for item in items
    ]

    result = collection.bulk_write(operations)
    client.close()
    return result.upserted_count + result.modified_count
