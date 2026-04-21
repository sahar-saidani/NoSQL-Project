from __future__ import annotations

from src.config import settings
from src.models import CatalogItem


CREATE_KEYSPACE = """
CREATE KEYSPACE IF NOT EXISTS {keyspace}
WITH replication = {{'class': 'SimpleStrategy', 'replication_factor': 1}}
"""

CREATE_TABLE = """
CREATE TABLE IF NOT EXISTS {keyspace}.catalog_items (
    external_id text PRIMARY KEY,
    source text,
    name text,
    category text,
    producer text,
    price double,
    rating double,
    stock int,
    description text,
    url text,
    tags list<text>
)
"""

INSERT_QUERY = """
INSERT INTO {keyspace}.catalog_items (
    external_id, source, name, category, producer,
    price, rating, stock, description, url, tags
) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
"""


class CassandraUnavailableError(RuntimeError):
    """Raised when the Cassandra driver cannot be initialized in this runtime."""


def _build_cluster():
    try:
        from cassandra.cluster import Cluster
    except Exception as exc:
        raise CassandraUnavailableError(
            "Le driver Cassandra est indisponible dans cet environnement. "
            "Sous Python 3.12+, installez une implementation de boucle supportee "
            "ou utilisez une version de Python compatible avec votre installation du driver."
        ) from exc

    return Cluster(contact_points=list(settings.cassandra_hosts), port=settings.cassandra_port)


def load_to_cassandra(items: list[CatalogItem]) -> int:
    if not items:
        return 0

    cluster = _build_cluster()
    session = cluster.connect()

    session.execute(CREATE_KEYSPACE.format(keyspace=settings.cassandra_keyspace))
    session.execute(CREATE_TABLE.format(keyspace=settings.cassandra_keyspace))
    prepared = session.prepare(INSERT_QUERY.format(keyspace=settings.cassandra_keyspace))

    for item in items:
        session.execute(
            prepared,
            (
                item.external_id,
                item.source,
                item.name,
                item.category,
                item.producer,
                item.price,
                item.rating,
                item.stock,
                item.description,
                item.url,
                item.tags,
            ),
        )

    session.shutdown()
    cluster.shutdown()
    return len(items)
