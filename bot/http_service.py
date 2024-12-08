from venv import logger

import requests
import json
from dataclasses import dataclass

from app.models import PrizeModel

class DobryHttpService:

    def __init__(self):
        self._url = self.Url()

    def get_prizes_list(self) -> list[PrizeModel]:
        http_method = 'prizes/'
        try:
            response = self._get(http_method)
        except Exception:
            logger.error('Unable to get list prizes')
            return []
        prizes = [PrizeModel(**item) for item in json.loads(response.content)]
        return prizes

    def _get(self, method_uri) -> requests.Response | None:
        url = f'{self._url.get_url()}/{method_uri}'
        response = requests.get(url)
        return response

    def _post(self, method_uri) -> requests.Response | None:
        url = f'{self._url.get_url()}/{method_uri}'
        response = requests.post(url)
        return response

    @dataclass
    class Url:
        protocol = 'http'
        domain = '127.0.0.1'
        port = '2444'
        api = 'api'

        def get_url(self) -> str:
            return f'{self.protocol}://{self.domain}:{self.port}/{self.api}'