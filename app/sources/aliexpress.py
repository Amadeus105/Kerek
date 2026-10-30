"""Поиск через AliExpress Affiliate API (метод aliexpress.affiliate.product.query).

Ключи берутся на portals.aliexpress.com -> API. Пока ключей нет,
этот модуль не используется. Код написан по документации и ещё
не проверялся на живых ключах.
"""

import hashlib
import hmac
import logging
import time

import httpx

from .. import config
from . import Product

log = logging.getLogger(__name__)

API_URL = "https://api-sg.aliexpress.com/sync"


def _sign(params: dict[str, str]) -> str:
    payload = "".join(f"{k}{params[k]}" for k in sorted(params))
    return hmac.new(config.ALI_APP_SECRET.encode(), payload.encode(), hashlib.sha256).hexdigest().upper()


async def search(query: str, limit: int = 40) -> list[Product]:
    params = {
        "method": "aliexpress.affiliate.product.query",
        "app_key": config.ALI_APP_KEY,
        "sign_method": "sha256",
        "timestamp": str(int(time.time() * 1000)),
        "keywords": query or "одежда",
        "target_currency": "USD",
        "target_language": "RU",
        "ship_to_country": "KZ",
        "page_size": str(min(limit, 50)),
    }
    if config.ALI_TRACKING_ID:
        params["tracking_id"] = config.ALI_TRACKING_ID
    params["sign"] = _sign(params)

    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.post(API_URL, data=params)
        resp.raise_for_status()
    data = resp.json()

    try:
        result = data["aliexpress_affiliate_product_query_response"]["resp_result"]["result"]
        items = result["products"]["product"]
    except (KeyError, TypeError):
        log.warning("Неожиданный ответ AliExpress: %s", str(data)[:500])
        return []

    products = []
    for it in items:
        try:
            price = float(it.get("target_sale_price") or it.get("sale_price"))
        except (TypeError, ValueError):
            continue
        rating = it.get("evaluate_rate", "").rstrip("%")
        products.append(
            Product(
                id=str(it.get("product_id")),
                title=it.get("product_title", ""),
                price=price,
                currency=it.get("target_sale_price_currency") or "USD",
                url=it.get("promotion_link") or it.get("product_detail_url", ""),
                source="AliExpress",
                image=it.get("product_main_image_url"),
                lang="ru",
                rating=round(float(rating) / 20, 1) if rating else None,  # 96% -> 4.8
                orders=it.get("lastest_volume"),
            )
        )
    return products
