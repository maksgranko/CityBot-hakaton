# STATIC API: https://yandex.ru/dev/staticapi/doc/ru/request

import requests
from urllib.parse import urlencode


class StaticAPI:
    BASE_URL = "https://static-maps.yandex.ru/v1"

    def __init__(self, api_key):
        self.api_key = api_key

    def get_static_map(self, ll, spn=None, bbox=None, z=15, size="600,600", scale=None, pt=None, pl=None, lang="ru_RU", style=None, theme=None, maptype="map"):
        params = {
            "apikey": self.api_key,
            "ll": ll,
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
            response = requests.get(url)
            response.raise_for_status()
            return response.content
        except requests.exceptions.RequestException as e:
            print(f"Error fetching static map: {e}")
            return None
