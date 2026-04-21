from __future__ import annotations

from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

from src.config import settings
from src.models import CatalogItem
from src.transformers import normalize_item


RATING_MAP = {
    "One": 1.0,
    "Two": 2.0,
    "Three": 3.0,
    "Four": 4.0,
    "Five": 5.0,
}


def _parse_price(value: str) -> float | None:
    cleaned = (
        value.replace("£", "")
        .replace("Â", "")
        .replace("$", "")
        .strip()
    )
    try:
        return float(cleaned)
    except ValueError:
        return None


def _extract_category_links() -> list[tuple[str, str]]:
    response = requests.get(settings.web_base_url, timeout=30)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")
    links: list[tuple[str, str]] = []

    for anchor in soup.select(".side_categories ul li ul li a"):
        name = anchor.get_text(strip=True)
        href = anchor.get("href", "")
        links.append((name, urljoin(settings.web_base_url, href)))

    return links


def fetch_web_items(limit: int = 20) -> list[CatalogItem]:
    items: list[CatalogItem] = []

    for category_name, category_url in _extract_category_links():
        if len(items) >= limit:
            break

        response = requests.get(category_url, timeout=30)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")
        for article in soup.select("article.product_pod"):
            if len(items) >= limit:
                break

            anchor = article.select_one("h3 a")
            price_node = article.select_one(".price_color")
            rating_node = article.select_one("p.star-rating")
            stock_node = article.select_one(".availability")

            book_url = urljoin(category_url, anchor.get("href", "")) if anchor else category_url
            book_name = anchor.get("title", "Unknown book") if anchor else "Unknown book"
            rating_classes = rating_node.get("class", []) if rating_node else []
            rating = next((RATING_MAP[value] for value in rating_classes if value in RATING_MAP), None)
            stock = 1 if stock_node and "In stock" in stock_node.get_text(" ", strip=True) else 0

            items.append(
                normalize_item(
                    {
                        "external_id": book_url,
                        "source": "web",
                        "name": book_name,
                        "category": category_name,
                        "producer": "Books to Scrape",
                        "price": _parse_price(price_node.get_text(strip=True)) if price_node else None,
                        "rating": rating,
                        "stock": stock,
                        "description": f"Book scraped from category {category_name}",
                        "url": book_url,
                        "tags": [category_name, "scraping"],
                    }
                )
            )

    return items
