import os

from dotenv import load_dotenv

load_dotenv()

# AliExpress Affiliate API (portals.aliexpress.com). Пусто = демо-данные.
ALI_APP_KEY = os.getenv("ALI_APP_KEY", "")
ALI_APP_SECRET = os.getenv("ALI_APP_SECRET", "")
ALI_TRACKING_ID = os.getenv("ALI_TRACKING_ID", "")

# DeepL API Free. Пусто = названия не переводятся.
DEEPL_KEY = os.getenv("DEEPL_KEY", "")

# Наценка к цене в процентах (доставка, комиссия). 0 = чистая цена по курсу.
MARKUP_PERCENT = float(os.getenv("MARKUP_PERCENT", "0"))


def use_aliexpress() -> bool:
    return bool(ALI_APP_KEY and ALI_APP_SECRET)
