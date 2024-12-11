# STATIC API: https://yandex.ru/dev/staticapi/doc/ru/request

import requests
from datetime import datetime
from urllib.parse import urlencode


class StaticAPI:
    BASE_URL = "https://static-maps.yandex.ru/v1"

    def __init__(self, api_key):
        self.api_key = api_key

    def get_static_map(self, ll, spn=None, bbox=None, z=15, size="400,400", scale=None, pt=None, pl=None, lang="ru_RU", style=None, theme=None, maptype="map"):
        params = {
            "apikey": self.api_key,
            "ll": f"{ll[0]},{ll[1]}",
            "size": size,
            "lang": lang,
            "maptype": maptype
        }

        if spn:
            params["spn"] = spn
        if bbox:
            params["bbox"] = bbox
        if z:
            params["z"] = z
        if scale:
            params["scale"] = scale
        if pt:
            params["pt"] = pt
        if pl:
            params["pl"] = pl
        if style:
            params["style"] = style
        if theme:
            params["theme"] = theme

        url = f"{self.BASE_URL}?{urlencode(params)}"
        try:
            print(url)
            response = requests.get(url)
            response.raise_for_status()
            return response.content
        except requests.exceptions.RequestException as e:
            print(f"Error fetching static map: {e}")
            return None

    def get_time_map(self, force_theme=None):
        if force_theme:
            return force_theme.lower()

        current_hour = datetime.now().hour

        if 6 <= current_hour < 18:
            return None
        else:
            return "dark"


    def get_map_time_based(self, ll, spn=None, bbox=None, z=15, size="400,400", scale=None, pt=None, pl=None,
                           lang="ru_RU", style=None, maptype="map", force_theme=None):
        theme = self.get_time_map(force_theme)
        return self.get_static_map(ll, spn, bbox, z, size, scale, pt, pl, lang, style, theme, maptype)
