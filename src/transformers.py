from __future__ import annotations

import re

from src.models import CatalogItem


def slugify(value: str) -> str:
    normalized = re.sub(r"[^a-zA-Z0-9]+", "-", value.strip().lower())
    return normalized.strip("-") or "unknown"


def normalize_text(value: str | None, fallback: str = "unknown") -> str:
    if not value:
        return fallback
    return " ".join(value.split()).strip()


def build_item_id(source: str, external_id: str) -> str:
    return f"{slugify(source)}::{slugify(external_id)}"


def normalize_item(payload: dict) -> CatalogItem:
    source = normalize_text(payload.get("source"), "unknown")
    external_id = normalize_text(payload.get("external_id"), "unknown")

    tags = payload.get("tags") or []
    if isinstance(tags, str):
        tags = [tags]

    item = CatalogItem(
        external_id=build_item_id(source, external_id),
        source=source,
        name=normalize_text(payload.get("name"), "Unnamed item"),
        category=normalize_text(payload.get("category")),
        producer=normalize_text(payload.get("producer")),
        price=float(payload["price"]) if payload.get("price") is not None else None,
        rating=float(payload["rating"]) if payload.get("rating") is not None else None,
        stock=int(payload["stock"]) if payload.get("stock") is not None else None,
        description=normalize_text(payload.get("description"), ""),
        url=normalize_text(payload.get("url"), ""),
        tags=[normalize_text(tag) for tag in tags if normalize_text(tag, "")],
    )
    return item
