import random

from vk_api import VkApi
from vk_api.longpoll import VkLongPoll

from .middleware import MiddlewareContainer


class PatchedLongpoll(VkLongPoll):
    def __init__(self, *args, **kwargs):
        self.group_id = kwargs.pop('group_id', None)
        super().__init__(*args, **kwargs)

    def update_longpoll_server(self, update_ts=True):
        values = {
            'lp_version': '3',
            'need_pts': self.pts
        }

        if self.group_id:
            values['group_id'] = self.group_id

        response = self.vk.method('messages.getLongPollServer', values)

        self.key = response['key']
        self.server = response['server']

        self.url = 'https://' + self.server

        if update_ts:
            self.ts = response['ts']
            if self.pts:
                self.pts = response['pts']


class Bot(MiddlewareContainer):
    def __init__(self):
        super().__init__()
        self.vk = None
        self.api = None
        self.group_id = None

    def connect(self, **kwargs):
        self.group_id = kwargs.pop('group_id', None)
        self.vk = VkApi(**kwargs)
        self.api = self.vk.get_api()

    def start_polling(self, **kwargs):
        kwargs.setdefault('mode', 0)
        poll = PatchedLongpoll(self.vk, **kwargs, group_id=self.group_id)

        for event in poll.listen():
            event.bot = self
            self.run_middleware(event)

    def send(self, **kwargs):
        """messages.send"""

        kwargs.setdefault('random_id', random.randint(-2147483648, 2147483647))

        if self.group_id:
            kwargs.setdefault('group_id', self.group_id)

        return self.api.messages.send(**kwargs)
        # FIXME: it's unclear to me how to send the literal sequence '<br>'

    def get_messages(self, **kwargs):
        """messages.getById"""

        if self.group_id:
            kwargs.setdefault('group_id', self.group_id)

        return self.api.messages.getById(**kwargs)
