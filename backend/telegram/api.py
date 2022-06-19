import requests

from .settings import TOKEN, CHAT_ID


class TelegramAPI:

    def __init__(self) -> None:
        self.url_send_notification = 'https://api.telegram.org/bot' +\
                                      TOKEN + '/sendMessage?chat_id=' +\
                                      CHAT_ID + '&parse_mode=Markdown&text='

    def send_notification(self, message: str) -> None:
        requests.get(self.url_send_notification + message)
