from __future__ import annotations

from neo4j import GraphDatabase

from src.config import settings
from src.models import CatalogItem


CYPHER = """
MERGE (i:Item {external_id: $external_id})
SET i.name = $name,
    i.price = $price,
    i.rating = $rating,
    i.stock = $stock,
    i.description = $description,
    i.url = $url,
    i.tags = $tags
MERGE (c:Category {name: $category})
MERGE (p:Producer {name: $producer})
MERGE (s:Source {name: $source})
MERGE (i)-[:BELONGS_TO]->(c)
MERGE (i)-[:PRODUCED_BY]->(p)
MERGE (i)-[:INGESTED_FROM]->(s)
"""


def load_to_neo4j(items: list[CatalogItem]) -> int:
    if not items:
        return 0

    driver = GraphDatabase.driver(
        settings.neo4j_uri,
        auth=(settings.neo4j_user, settings.neo4j_password),
    )

    with driver.session() as session:
        for item in items:
            session.run(CYPHER, item.to_dict())

    driver.close()
    return len(items)
