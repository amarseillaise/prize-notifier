import requests
import json
from dataclasses import dataclass
from logging import log

from app.models import PrizeModel

class DobryHttpService:

    def __init__(self):
        self._url = self.Url()

    def get_prizes_list(self) -> list[PrizeModel]:
        http_method = 'prizes/'
        response = self._get(http_method)
        if not response:
            return []
        prizes = [PrizeModel(**item) for item in json.loads(response.content)]
        return prizes

    def _get(self, method_uri) -> requests.Response | None:
        url = f'{self._url.get_url()}/{method_uri}'
        response = self._make_request(requests.get, url=url)
        return response

    def _post(self, method_uri) -> requests.Response | None:
        url = f'{self._url.get_url()}/{method_uri}'
        response = self._make_request(requests.post, url=url)
        return response

    def _make_request(self, method, **kwargs) -> requests.Response | None:
        response = self._try_request(method, **kwargs)
        if response and response.status_code != 200:
            return None
        return response

    def _try_request(self, method, **kwargs) -> requests.Response | None:
        try:
            return method(**kwargs)
        except Exception as e:
            log(0, str(e), exc_info=e)
            return None

    @dataclass
    class Url:
        protocol = 'http'
        domain = '127.0.0.1'
        port = '2444'
        api = 'api'

        def get_url(self) -> str:
            return f'{self.protocol}://{self.domain}:{self.port}/{self.api}'