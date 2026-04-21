from __future__ import annotations

import argparse
import json
import sys

from src.extractors.web_source import fetch_web_items
from src.loaders.cassandra_loader import CassandraUnavailableError
from src.loaders.cassandra_loader import load_to_cassandra
from src.loaders.mongo_loader import load_to_mongodb
from src.loaders.neo4j_loader import load_to_neo4j


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Pipeline ETL: Web scraping -> MongoDB -> Cassandra -> Neo4j"
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=20,
        help="Nombre maximal d'elements a extraire",
    )
    parser.add_argument(
        "--extract-only",
        action="store_true",
        help="Extraire et afficher les donnees sans chargement en base",
    )
    return parser.parse_args()


def extract_items(limit: int):
    return fetch_web_items(limit=limit)


def run_loader(name: str, loader, items) -> tuple[int, str]:
    try:
        return loader(items), "ok"
    except CassandraUnavailableError as exc:
        print(f"[avertissement] {name} ignore: {exc}", file=sys.stderr)
        return 0, "ignore"


def main() -> None:
    args = parse_args()
    items = extract_items(args.limit)

    if args.extract_only:
        print(json.dumps([item.to_dict() for item in items], indent=2, ensure_ascii=True))
        return

    mongo_count, _ = run_loader("MongoDB", load_to_mongodb, items)
    cassandra_count, cassandra_status = run_loader("Cassandra", load_to_cassandra, items)
    neo4j_count, _ = run_loader("Neo4j", load_to_neo4j, items)

    print("Source utilisee      : web scraping")
    print(f"Elements extraits    : {len(items)}")
    print(f"MongoDB charges      : {mongo_count}")
    cassandra_label = f"{cassandra_count}"
    if cassandra_status != "ok":
        cassandra_label = f"{cassandra_label} ({cassandra_status})"
    print(f"Cassandra charges    : {cassandra_label}")
    print(f"Neo4j charges        : {neo4j_count}")


if __name__ == "__main__":
    main()
