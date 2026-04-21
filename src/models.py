from __future__ import annotations

from dataclasses import asdict, dataclass, field


@dataclass(slots=True)
class CatalogItem:
    external_id: str
    source: str
    name: str
    category: str
    producer: str
    price: float | None = None
    rating: float | None = None
    stock: int | None = None
    description: str = ""
    url: str = ""
    tags: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return asdict(self)
