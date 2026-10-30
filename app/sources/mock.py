"""Демо-товары, пока не подключён AliExpress API. Цены в юанях."""

from urllib.parse import quote

from . import Product

_RAW = [
    ("Брюки карго мужские свободного кроя", 89, "men", "pants", ["M", "L", "XL"], ["хаки", "чёрный"], 4.8, 5320, "штаны брюки карго"),
    ("Джинсы мужские прямые, плотный деним", 119, "men", "pants", ["S", "M", "L", "XL"], ["синий"], 4.7, 2140, "штаны джинсы"),
    ("Спортивные штаны мужские джоггеры", 59, "men", "pants", ["M", "L", "XL", "XXL"], ["серый", "чёрный"], 4.6, 8810, "штаны джоггеры спортивные"),
    ("Брюки чинос мужские хлопок", 99, "men", "pants", ["M", "L"], ["бежевый", "тёмно-синий"], 4.5, 960, "штаны брюки классические"),
    ("Широкие брюки женские с высокой талией", 79, "women", "pants", ["S", "M", "L"], ["чёрный", "молочный"], 4.7, 6400, "штаны брюки палаццо"),
    ("Джинсы женские mom fit", 109, "women", "pants", ["XS", "S", "M"], ["голубой"], 4.6, 3100, "штаны джинсы"),
    ("Футболка оверсайз мужская, 100% хлопок", 39, "men", "tshirt", ["M", "L", "XL"], ["белый", "чёрный", "оливковый"], 4.8, 12500, "футболка майка"),
    ("Футболка женская базовая приталенная", 29, "women", "tshirt", ["XS", "S", "M", "L"], ["белый", "розовый"], 4.6, 7300, "футболка майка"),
    ("Куртка мужская демисезонная ветровка", 189, "men", "jacket", ["L", "XL", "XXL"], ["чёрный", "хаки"], 4.7, 1800, "куртка ветровка"),
    ("Пуховик мужской зимний до -30", 359, "men", "jacket", ["M", "L", "XL"], ["чёрный"], 4.8, 2700, "куртка пуховик зимняя"),
    ("Пуховик женский удлинённый", 329, "women", "jacket", ["S", "M", "L"], ["бежевый", "чёрный"], 4.7, 1500, "куртка пуховик зимняя пальто"),
    ("Кроссовки мужские беговые лёгкие", 149, "men", "shoes", ["41", "42", "43", "44"], ["белый", "серый"], 4.6, 4200, "обувь кроссовки"),
    ("Кеды женские на платформе", 99, "women", "shoes", ["36", "37", "38", "39"], ["белый"], 4.5, 3900, "обувь кеды"),
    ("Рюкзак городской с отделением для ноутбука", 129, "men", "bag", [], ["чёрный", "серый"], 4.8, 6100, "рюкзак сумка"),
    ("Сумка женская через плечо, экокожа", 89, "women", "bag", [], ["чёрный", "коричневый"], 4.6, 2900, "сумка"),
    ("Штаны детские утеплённые на флисе", 55, "kids", "pants", ["110", "120", "130", "140"], ["синий", "серый"], 4.7, 2300, "штаны брюки детские"),
]

PRODUCTS = [
    Product(
        id=f"demo-{i}",
        title=title,
        price=price,
        currency="CNY",
        url="https://www.aliexpress.com/w/wholesale-" + quote(tags.split()[0]) + ".html",
        source="Демо",
        category=cat,
        kind=kind,
        sizes=sizes,
        colors=colors,
        rating=rating,
        orders=orders,
    )
    for i, (title, price, cat, kind, sizes, colors, rating, orders, tags) in enumerate(_RAW)
]
_TAGS = {f"demo-{i}": row[-1] for i, row in enumerate(_RAW)}


def _stem(word: str) -> str:
    # Грубо отрезаем окончание: "мужские" -> "мужск", "штаны" -> "штан".
    return word[: max(3, min(len(word) - 1, 5))]


async def search(query: str, limit: int = 40) -> list[Product]:
    words = [_stem(w) for w in query.lower().split() if len(w) >= 3]
    if not words:
        return PRODUCTS[:limit]

    def haystack(p: Product) -> str:
        cat = {"men": "мужской мужская мужские", "women": "женский женская женские", "kids": "детский детские"}
        return f"{p.title} {_TAGS[p.id]} {cat.get(p.category, '')}".lower()

    all_match = [p for p in PRODUCTS if all(w in haystack(p) for w in words)]
    if all_match:
        return all_match[:limit]
    return [p for p in PRODUCTS if any(w in haystack(p) for w in words)][:limit]
