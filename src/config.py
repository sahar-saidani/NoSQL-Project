from __future__ import annotations

import os
from dataclasses import dataclass

from dotenv import load_dotenv


load_dotenv()


@dataclass(frozen=True)
class Settings:
    mongo_uri: str = os.getenv("MONGO_URI", "mongodb://localhost:27017")
    mongo_database: str = os.getenv("MONGO_DATABASE", "nosql_project")
    mongo_collection: str = os.getenv("MONGO_COLLECTION", "items")

    cassandra_hosts: tuple[str, ...] = tuple(
        host.strip()
        for host in os.getenv("CASSANDRA_HOSTS", "127.0.0.1").split(",")
        if host.strip()
    )
    cassandra_port: int = int(os.getenv("CASSANDRA_PORT", "9042"))
    cassandra_keyspace: str = os.getenv("CASSANDRA_KEYSPACE", "nosql_project")

    neo4j_uri: str = os.getenv("NEO4J_URI", "bolt://localhost:7687")
    neo4j_user: str = os.getenv("NEO4J_USER", "neo4j")
    neo4j_password: str = os.getenv("NEO4J_PASSWORD", "password123")

    web_base_url: str = os.getenv("WEB_BASE_URL", "https://books.toscrape.com")


settings = Settings()
