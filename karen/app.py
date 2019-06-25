# TODO: improve imports style
# TODO: build docker image
# TODO: implement commands
# TODO: implement admin notification
# TODO: better logging
# TODO: think about handling attachments
# FIXME: comment the code (an everlasting problem)

import traceback
import html

from vk_api.longpoll import VkLongpollMode

from . import globals as g
from . import config
from . import tracking, commands


def handle_errors(event, next):
    try:
        next()
    except Exception:
        traceback.print_exc()
        # self.send({
        #     'user_id': config.ADMIN_ID,
        #     'text': err,
        # })


def preprocess_event(event, next):
    print(event.raw)
    if hasattr(event, 'text'):
        event.text = html.unescape(event.text)
    next()


g.bot.use(
    handle_errors,
    preprocess_event,
    tracking.message_new,
    tracking.message_edited,
    tracking.message_deleted,
)

# App entrypoint
if __name__ == '__main__':
    g.bot.connect(token=config.ACCESS_TOKEN,
                  group_id=config.GROUP_ID, api_version=config.API_VERSION)
    g.bot.start_polling(mode=VkLongpollMode.GET_EXTENDED)
