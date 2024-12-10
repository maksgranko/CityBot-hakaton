# GEOCODER API: https://yandex.ru/dev/geocode/doc/ru/

import requests

class Geocoder:
    BASE_URL = "https://geocode-maps.yandex.ru/1.x/"

    def __init__(self, api_key):
        self.api_key = api_key

    def make_request(self, geocode, lang="ru_RU", kind=None, rspn=0, ll=None, spn=None, bbox=None, results=10, skip=0,
                     format="json"):
        params = {
            "apikey": self.api_key,
            "geocode": geocode,
            "lang": lang,
            "format": format,
            "rspn": rspn,
            "results": results,
            "skip": skip
        }

        if kind:
            params["kind"] = kind
        if ll:
            params["ll"] = ll
        if spn:
            params["spn"] = spn
        if bbox:
            params["bbox"] = bbox

        try:
            response = requests.get(self.BASE_URL, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error making request: {e}")
            return None

    def geocode_address(self, address, lang="ru_RU", results=1):
        response = self.make_request(geocode=address, lang=lang, results=results)
        if response:
            try:
                pos = response["response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"]["Point"]["pos"]
                return tuple(map(float, pos.split()))
            except (KeyError, IndexError, ValueError):
                print("Unable to parse response for geocode address.")
        return None

    def reverse_geocode(self, latitude, longitude, lang="ru_RU", kind=None):
        geocode = f"{longitude},{latitude}"
        response = self.make_request(geocode=geocode, lang=lang, kind=kind)
        if response:
            try:
                address = \
                response["response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"]["metaDataProperty"][
                    "GeocoderMetaData"]["text"]
                return address
            except (KeyError, IndexError):
                print("Unable to parse response for reverse geocode.")
        return None

    def get_linkByCoords(self,coords):
        x,y = coords
        return f"https://yandex.ru/maps/?whatshere%5Bpoint%5D={x}%2C{y}&z=15"

    def get_linkByAddress(self, address):
        x,y = tuple(self.geocode_address(address))
        return f"https://yandex.ru/maps/?whatshere%5Bpoint%5D={str(x)}%2C{str(y)}&z=15"