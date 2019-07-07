# TODO: add commands + some kind of help
# TODO: add admin notifications
# TODO: add laconic mode, love4love mode
# TODO: forgive typos
# TODO: think about persistence
# FIXME: comment the code (an everlasting problem)

import logging
import traceback

from vk_api.longpoll import VkLongpollMode

from . import config  # ensure it's loaded before anything else
from . import globals as g
from . import tracking

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


g.bot.use(
    handle_errors,
    tracking.message_new,
    tracking.message_edited,
    tracking.message_deleted,
)


def main():
    """App entrypoint"""

    logger.info('Starting bot')
    g.bot.connect(token=config.ACCESS_TOKEN,
                  group_id=config.GROUP_ID, api_version=config.API_VERSION)
    g.bot.start_polling()
