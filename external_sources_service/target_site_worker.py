import requests
import json
from dataclasses import dataclass

from app import models
from fake_useragent import UserAgent

class RequestWorker:

    def __init__(self, username: str, password: str):
        self.session = requests.Session()
        self.username = username
        self.password = password
        self.url = RequestWorker.Url()
        self._init_headers()

    def authenticate(self) -> bool:
        http_method = 'oauth/token'
        url = self._build_url(self.url.get_url(), http_method)
        http_response = self.session.post(url=url, data=self._get_raw_auth_data())
        if http_response.status_code == 200:
            response_model = models.AuthResponseModel(**json.loads(http_response.content))
            if response_model.data:
                self._set_bearer_token(response_model.data.access_token)
                return True

    def get_prizes(self) -> list[dict]:
        http_method = 'private/prize/shop'
        url = self._build_url(self.url.get_url(), http_method)
        http_response = self.session.get(url)
        if http_response.status_code == 200:
            prizes = json.loads(http_response.content)
            return prizes.get('data', [])
        return []


    def _get_auth_data(self) -> dict[str, str]:
        return {'username': self.username, 'password': self.password}

    def _get_raw_auth_data(self) -> str:
        return json.dumps(self._get_auth_data())

    def _finish_worker_session(self) -> None:
        self.session.close()

    def _set_bearer_token(self, token) -> None:
        self.session.headers['authorization'] = f'Bearer {token}'

    def _init_headers(self):
        headers = {
            'accept': 'application/json',
            'accept-language': 'ru,en;q=0.9',
            'content-type': 'application/json',
            'user-agent': UserAgent().chrome
        }
        self.session.headers.update(headers)

    @staticmethod
    def _build_url(base_url: str, method: str):
        return f'{base_url}/{method}'

    @dataclass
    class Url:
        protocol = 'https'
        domain = 'dobrycola-promo.ru'
        api = 'backend'

        def get_url(self) -> str:
            return f'{self.protocol}://{self.domain}/{self.api}'