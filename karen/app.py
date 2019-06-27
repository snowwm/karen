# TODO: implement commands
# TODO: implement admin notification
# TODO: think about handling attachments
# FIXME: comment the code (an everlasting problem)

import traceback
import html
import logging

from vk_api.longpoll import VkLongpollMode

from . import config  # ensure it's loaded before anything else
from . import globals as g
from . import tracking, commands

logger = logging.getLogger(__name__)


def handle_errors(event, next):
    try:
        next()
    except Exception:
        logger.exception('In handler middleware:')
        # self.send({
        #     'user_id': config.ADMIN_ID,
        #     'text': err,
        # })


def preprocess_event(event, next):
    if hasattr(event, 'text'):
        event.text = html.unescape(event.text)  # TODO: send pull to upstream
    next()


g.bot.use(
    handle_errors,
    preprocess_event,
    tracking.message_new,
    tracking.message_edited,
    tracking.message_deleted,
)


def start():
    """App entrypoint"""

    logger.info('Starting bot')
    g.bot.connect(token=config.ACCESS_TOKEN,
                  group_id=config.GROUP_ID, api_version=config.API_VERSION)
    g.bot.start_polling(
        mode=int(VkLongpollMode.GET_EXTENDED))  # TODO: send pull


if __name__ == '__main__':
    start()
