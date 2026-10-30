"""Курсы валют к тенге с сайта Нацбанка РК."""

import asyncio
import logging
import time
import xml.etree.ElementTree as ET

import httpx

log = logging.getLogger(__name__)

RATES_URL = "https://nationalbank.kz/rss/rates_all.xml"
CACHE_SECONDS = 6 * 60 * 60

# Примерные курсы на случай, если сайт Нацбанка недоступен.
FALLBACK = {"USD": 510.0, "CNY": 71.0, "RUB": 6.3, "EUR": 590.0}

_cache: dict[str, float] = {}
_fetched_at = 0.0
_is_live = False
_lock = asyncio.Lock()


def _parse(xml_text: str) -> dict[str, float]:
    rates = {}
    for item in ET.fromstring(xml_text).iter("item"):
        code = (item.findtext("title") or "").strip()
        value = (item.findtext("description") or "").strip()
        quant = (item.findtext("quant") or "1").strip()
        try:
            rates[code] = float(value) / float(quant)
        except ValueError:
            continue
    return rates


async def get_rates() -> tuple[dict[str, float], bool]:
    """Возвращает (курсы, живые ли это данные)."""
    global _cache, _fetched_at, _is_live
    async with _lock:
        if _cache and time.time() - _fetched_at < CACHE_SECONDS:
            return _cache, _is_live
        try:
            async with httpx.AsyncClient(timeout=5) as client:
                resp = await client.get(RATES_URL)
                resp.raise_for_status()
            rates = _parse(resp.text)
            if "USD" not in rates:
                raise ValueError("в ответе нет USD")
            _cache, _is_live = rates, True
        except Exception as exc:  # сеть, формат, что угодно
            log.warning("Курсы Нацбанка недоступны, беру запасные: %s", exc)
            _cache, _is_live = dict(FALLBACK), False
        _fetched_at = time.time()
        return _cache, _is_live


async def to_kzt(amount: float, currency: str) -> float:
    if currency == "KZT":
        return amount
    rates, _ = await get_rates()
    rate = rates.get(currency) or FALLBACK.get(currency)
    if rate is None:
        raise ValueError(f"Нет курса для {currency}")
    return amount * rate
