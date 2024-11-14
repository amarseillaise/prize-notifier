import schedule
import time
import requests
import json
import os
from dataclasses import dataclass
from threading import Thread

from telebot import TeleBot, types, apihelper
from app.models import PrizeModel

current_thread = ...

class DobryPizeBotService:

    def __init__(self):
        self.polling_site_enabled = False
        self.all_prize_list = []
        self.wished_prizes = []
        self.url = self.Url()

    def init_commands(self, bot: TeleBot):
        commands = [
            types.BotCommand('subscribe', description='Подписаться на обновления призов'),
            types.BotCommand('unsubscribe', description='Отписаться от обновления призов'),
            types.BotCommand('list_prize', description='Список всех возможных призов'),
            types.BotCommand('wishlist', description='Показать отслеживаемые призы'),
            types.BotCommand('add_to_wishlist', description='Добавить приз в отслеживаемые'),
            types.BotCommand('remove_from_wishlist', description='Удалить приз из отслеживаемых'),
        ]
        bot.set_my_commands(commands)

    def start(self, chat: types.Chat):
        pass

    def stop(self, chat: types.Chat):
        self._remove_user_from_subscribers(chat.id)

    def subscribe(self, bot: TeleBot, chat_message: types.Message):
        global current_thread
        self._add_user_to_subscribers(chat_message.chat.id, chat_message.chat.username)
        bot.send_message(chat_message.chat.id, 'При появление приза из списка отслеживаемых придёт уведомление')
        if self.check_start_site_polling():
            self.start_prizes_polling(bot)

    def unsubscribe(self, bot: TeleBot, chat_message: types.Message):
        self._remove_user_from_subscribers(chat_message.chat.id)
        bot.send_message(chat_message.chat.id, 'Изменение статуса призов больше не отслеживается')

    def send_prizes_list(self, bot: TeleBot, chat_message: types.Message):
        http_method = 'prizes/'
        url = f'{self.url.get_url()}/{http_method}'
        response = requests.get(url)
        prizes = [PrizeModel(**item) for item in json.loads(response.content)]
        message = self._get_all_prizes_formated(prizes)
        bot.send_message(chat_message.chat.id, message)

    def send_wishlist(self, bot: TeleBot, chat_message: types.Message):
        wishlist_dict = self._get_wishlist()
        wishlist = [PrizeModel(**item) for item in wishlist_dict.values()]
        message = self._get_wishlist_formated(wishlist)
        bot.send_message(chat_message.chat.id, message)

    def add_prize_to_wishlist(self, bot: TeleBot, chat_message: types.Message):
        http_method = 'prizes/'
        url = f'{self.url.get_url()}/{http_method}'
        response = requests.get(url)
        prizes = [PrizeModel(**item) for item in json.loads(response.content)]
        self.all_prize_list = prizes
        message = self._get_all_prizes_formated_by_id_to_add(prizes)
        bot.send_message(chat_message.chat.id, message)
        bot.register_next_step_handler(chat_message, self._handle_add_to_wishlist, bot=bot)

    def remove_prize_from_wishlist(self, bot: TeleBot, chat_message: types.Message):
        prizes_dict = self._get_wishlist()
        prizes = [PrizeModel(**item) for item in prizes_dict.values()]
        self.wished_prizes = prizes
        message = self._get_all_prizes_formated_by_id_to_delete(prizes)
        bot.send_message(chat_message.chat.id, message)
        bot.register_next_step_handler(chat_message, self._handle_delete_from_wishlist, bot=bot)

    def check_start_site_polling(self) -> bool:
        return self._has_subscribers() and self._has_wishlist() and not self.polling_site_enabled

    def _check_prizes_available(self, bot: TeleBot):
        http_method = 'prizes/'
        url = f'{self.url.get_url()}/{http_method}'
        response = requests.get(url)
        all_prizes = [PrizeModel(**item) for item in json.loads(response.content)]
        wished_prizes = self._get_wishlist()
        available_prizes = [prize for prize in all_prizes if prize.is_available() and str(prize.id) in wished_prizes]
        if available_prizes:
            message = self._get_available_prizes_formated(available_prizes)
            self._send_message_to_subscribers(message, bot)

    def start_prizes_polling(self, bot: TeleBot):
        global current_thread
        current_thread = Thread(target=self._run_thread_prizes_polling, kwargs={'bot': bot})
        current_thread.start()

    def _run_thread_prizes_polling(self, bot: TeleBot):
        timeout = int(os.getenv('POLLING_TIMEOUT_MINUTES'))
        job = schedule.every(timeout).minutes.do(self._check_prizes_available, bot=bot)
        while self._has_subscribers() and self._has_wishlist():
            self.polling_site_enabled = True
            schedule.run_pending()
            time.sleep(1)
        self.polling_site_enabled = False
        schedule.cancel_job(job)

    def _handle_add_to_wishlist(self, message: types.Message, bot: TeleBot):
        choose_prize = self._get_prize_model_by_id(self.all_prize_list, message.text)
        if choose_prize:
            wishlist = self._get_wishlist()
            wishlist[str(choose_prize.id)] = choose_prize.model_dump()
            self._write_wishlist(wishlist)
            self.wished_prizes = [PrizeModel(**item) for item in wishlist.values()]
            bot.send_message(message.chat.id,f'Приз {choose_prize.name} успешно добавлен')
            if self.check_start_site_polling():
                self.start_prizes_polling(bot)
        else:
            bot.send_message(message.chat.id, 'Приз с таким ID не найден')

    def _handle_delete_from_wishlist(self, message: types.Message, bot: TeleBot):
        choose_prize = self._get_prize_model_by_id(self.wished_prizes, message.text)
        if choose_prize:
            wishlist = self._get_wishlist()
            wishlist.pop(str(choose_prize.id))
            self._write_wishlist(wishlist)
            self.wished_prizes = [PrizeModel(**item) for item in wishlist.values()]
            bot.send_message(message.chat.id,f'Приз {choose_prize.name} больше не отслеживается')
        else:
            bot.send_message(message.chat.id, 'Неверный ID')

    def _send_message_to_subscribers(self, message: str, bot: TeleBot):
        subscribers = self._get_subscribers()
        for subscriber_id in subscribers.keys():
            try:
                bot.send_message(subscriber_id, message)
            except apihelper.ApiTelegramException:
                self._remove_user_from_subscribers(subscriber_id)
            finally:
                continue

    def _add_user_to_subscribers(self, user_id, user_name) -> None:
        subscribers = self._get_subscribers()
        subscribers[str(user_id)] = str(user_name)
        self._write_subscribers(subscribers)

    def _remove_user_from_subscribers(self, user_id) -> None:
        subscribers = self._get_subscribers()
        subscribers.pop(str(user_id), None)
        self._write_subscribers(subscribers)

    def _has_subscribers(self) -> bool:
        return bool(self._get_subscribers())

    def _has_wishlist(self) -> bool:
        return bool(self._get_wishlist())

    @staticmethod
    def _get_subscribers() -> dict:
        file_path = './subscribers.json'
        if not os.path.exists(file_path):
            return {}
        with open(file=file_path, mode='r') as f:
            content = f.read()
            return json.loads(content)

    @staticmethod
    def _write_subscribers(data: dict) -> None:
        file_path = './subscribers.json'
        with open(file=file_path, mode='w') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

    @staticmethod
    def _get_wishlist() -> dict:
        file_path = './wishlist.json'
        if not os.path.exists(file_path):
            return {}
        with open(file=file_path, mode='r') as f:
            content = f.read()
            return json.loads(content)

    @staticmethod
    def _write_wishlist(data: dict) -> None:
        file_path = './wishlist.json'
        with open(file=file_path, mode='w') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

    @staticmethod
    def _get_prize_model_by_id(all_prizes: list[PrizeModel], prize_id: str) -> PrizeModel | None:
        for prize in all_prizes:
            if str(prize.id) == prize_id:
                return prize

    @staticmethod
    def _get_all_prizes_formated(prizes: list[PrizeModel]) -> str:
        return '\n'.join([f"{item.name} - {'доступно ✅' if item.is_available() else 'закончилось ❌'}"
                          for item in prizes])
    @staticmethod
    def _get_all_prizes_formated_by_id_to_add(prizes: list[PrizeModel]) -> str:
        text = 'Введи ID приза, появление которого надо отслеживать:\n\n'
        return text + '\n'.join([f"{item.id} - {item.name}" for item in prizes if not item.is_available()])

    @staticmethod
    def _get_all_prizes_formated_by_id_to_delete(prizes: list[PrizeModel]) -> str:
        text = 'Введи ID приза, который больше не нужно отслеживать:\n\n'
        return text + '\n'.join([f"{item.id} - {item.name}" for item in prizes])

    @staticmethod
    def _get_wishlist_formated(prizes: list[PrizeModel]) -> str:
        text = 'Сейчас отслеживается появление следующих призов:\n\n'
        return text + '\n'.join([f"{item.id} - {item.name}" for item in prizes])

    @staticmethod
    def _get_available_prizes_formated(prizes: list[PrizeModel]) -> str:
        text = 'Срочно! Срочно! Срочно! Доступны для заказа следующие призы:\n\n'
        site = '\n\nhttps://dobrycola-promo.ru/profile'
        return text + '\n'.join([item.name for item in prizes]) + site

    @dataclass
    class Url:
        protocol = 'http'
        domain = '127.0.0.1'
        port = '2444'
        api = 'api'

        def get_url(self) -> str:
            return f'{self.protocol}://{self.domain}:{self.port}/{self.api}'