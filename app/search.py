"""Поиск: источник -> перевод -> цена в тенге -> фильтры -> сортировка."""

import logging
from dataclasses import dataclass

from . import config, rates, translate
from .sources import Product, aliexpress, mock

log = logging.getLogger(__name__)

SORTS = {
    "relevance": "По релевантности",
    "cheap": "Сначала дешёвые",
    "expensive": "Сначала дорогие",
    "popular": "По числу заказов",
}


@dataclass
class Filters:
    q: str = ""
    category: str = ""
    size: str = ""
    max_price: int | None = None
    sort: str = "relevance"


async def run(f: Filters) -> list[Product]:
    if config.use_aliexpress():
        try:
            products = await aliexpress.search(f.q)
        except Exception as exc:
            log.error("AliExpress упал, показываю демо: %s", exc)
            products = await mock.search(f.q)
    else:
        products = await mock.search(f.q)

    foreign = [p for p in products if p.lang != "ru"]
    for p, title in zip(foreign, await translate.to_russian([p.title for p in foreign])):
        p.title, p.lang = title, "ru"

    markup = 1 + config.MARKUP_PERCENT / 100
    for p in products:
        p.price_kzt = round(await rates.to_kzt(p.price, p.currency) * markup)

    if f.category:
        products = [p for p in products if not p.category or p.category == f.category]
    if f.size:
        products = [p for p in products if not p.sizes or f.size.upper() in p.sizes]
    if f.max_price:
        products = [p for p in products if p.price_kzt <= f.max_price]

    if f.sort == "cheap":
        products.sort(key=lambda p: p.price_kzt)
    elif f.sort == "expensive":
        products.sort(key=lambda p: -p.price_kzt)
    elif f.sort == "popular":
        products.sort(key=lambda p: -(p.orders or 0))
    return products
