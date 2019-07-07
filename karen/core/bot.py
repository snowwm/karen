import logging

from vk_api import VkApi, utils
from vk_api.longpoll import VkLongPoll

from .middleware import MiddlewareContainer

logger = logging.getLogger(__name__)


class Bot(MiddlewareContainer):
    def __init__(self):
        super().__init__()
        self.vk = None
        self.api = None
        self.group_id = None

    def connect(self, group_id=None, **kwargs):
        self.group_id = group_id
        self.vk = VkApi(**kwargs)
        self.api = self.vk.get_api()
        logger.info('Connected')

    def start_polling(self, mode=0, **kwargs):
        poll = VkLongPoll(self.vk, mode=mode, group_id=self.group_id, **kwargs)

        logger.info('Starting the poll')
        for event in poll.listen():
            logger.debug('Received event: %s', event.raw)
            event._bot = self
            self.run_middleware(event)

    def send(self, **kwargs):
        """messages.send"""

        kwargs.setdefault('random_id', utils.get_random_id())

        if self.group_id:
            kwargs.setdefault('group_id', self.group_id)

        logger.debug('Sending message: %s', kwargs)
        return self.api.messages.send(**kwargs)
        # it's unclear to me how to send the literal sequence '<br>'

    def get_messages(self, **kwargs):
        """messages.getById"""

        if self.group_id:
            kwargs.setdefault('group_id', self.group_id)

        res = self.api.messages.getById(**kwargs)
        logger.debug('Received messages: %s', res)
        return res
