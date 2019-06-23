import random

from vk_api import VkApi
from vk_api.longpoll import VkLongPoll

from .middleware import MiddlewareContainer


class Bot(MiddlewareContainer):
    def __init__(self, **kwargs):
        super().__init__()
        self.vk = None
        self.api = None

    def connect(self, **kwargs):
        self.vk = VkApi(**kwargs)
        self.api = self.vk.get_api()

    def start_polling(self, **kwargs):
        kwargs.setdefault('mode', 0)
        poll = VkLongPoll(self.vk, **kwargs)

        for event in poll.listen():
            event.bot = self
            self.run_middleware(event)

    def send(self, options):
        options.setdefault(
            'random_id', random.randint(-2147483648, 2147483647))
        self.api.messages.send(**options)
        # FIXME: it's unclear to me how to send the literal sequence '<br>'
