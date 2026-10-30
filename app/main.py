from dataclasses import asdict
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from . import config, rates, search

BASE = Path(__file__).parent
app = FastAPI(title="Керек")
app.mount("/static", StaticFiles(directory=BASE / "static"), name="static")
templates = Jinja2Templates(directory=BASE / "templates")

SIZES = ["XS", "S", "M", "L", "XL", "XXL"]
CATEGORIES = {"": "Все", "men": "Мужское", "women": "Женское", "kids": "Детское"}


def _filters(q: str, category: str, size: str, max_price: str, sort: str) -> search.Filters:
    digits = "".join(ch for ch in max_price if ch.isdigit())
    return search.Filters(
        q=q.strip()[:100],
        category=category if category in CATEGORIES else "",
        size=size if size in SIZES else "",
        max_price=int(digits) if digits else None,
        sort=sort if sort in search.SORTS else "relevance",
    )


@app.get("/", response_class=HTMLResponse)
async def index(request: Request, q: str = "", category: str = "", size: str = "", max_price: str = "", sort: str = "relevance"):
    f = _filters(q, category, size, max_price, sort)
    products = await search.run(f)
    rate_table, live = await rates.get_rates()
    return templates.TemplateResponse(
        request,
        "index.html",
        {
            "f": f,
            "products": products,
            "sizes": SIZES,
            "categories": CATEGORIES,
            "sorts": search.SORTS,
            "cny": rate_table.get("CNY"),
            "usd": rate_table.get("USD"),
            "rates_live": live,
            "demo": not config.use_aliexpress(),
            "markup": config.MARKUP_PERCENT,
        },
    )


@app.get("/api/search")
async def api_search(q: str = "", category: str = "", size: str = "", max_price: str = "", sort: str = "relevance"):
    products = await search.run(_filters(q, category, size, max_price, sort))
    return {"count": len(products), "items": [asdict(p) for p in products]}


@app.get("/health")
async def health():
    return {"ok": True}
