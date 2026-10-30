from dataclasses import dataclass, field


@dataclass
class Product:
    id: str
    title: str
    price: float  # в валюте магазина
    currency: str  # USD, CNY ...
    url: str
    source: str  # "AliExpress", "Демо"
    image: str | None = None
    lang: str = "ru"  # язык названия; не "ru" = переводим
    category: str = ""  # men / women / kids
    kind: str = ""  # pants / tshirt / jacket / shoes / bag
    sizes: list[str] = field(default_factory=list)
    colors: list[str] = field(default_factory=list)
    rating: float | None = None
    orders: int | None = None
    price_kzt: float = 0.0  # заполняется в search.py
