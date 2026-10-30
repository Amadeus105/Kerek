"""Перевод названий товаров на русский через DeepL API Free.

Переводы кэшируются в памяти, чтобы не платить дважды за одну строку.
Позже кэш стоит перенести в Postgres.
"""

import logging

import httpx

from . import config

log = logging.getLogger(__name__)

DEEPL_URL = "https://api-free.deepl.com/v2/translate"
_cache: dict[str, str] = {}


async def to_russian(texts: list[str]) -> list[str]:
    if not config.DEEPL_KEY or not texts:
        return texts

    missing = [t for t in dict.fromkeys(texts) if t not in _cache]
    if missing:
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                resp = await client.post(
                    DEEPL_URL,
                    headers={"Authorization": f"DeepL-Auth-Key {config.DEEPL_KEY}"},
                    json={"text": missing, "target_lang": "RU"},
                )
                resp.raise_for_status()
            for src, tr in zip(missing, resp.json()["translations"]):
                _cache[src] = tr["text"]
        except Exception as exc:
            log.warning("Перевод не удался, оставляю оригинал: %s", exc)
            return texts

    return [_cache.get(t, t) for t in texts]
