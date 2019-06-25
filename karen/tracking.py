from vk_api.longpoll import VkEventType, VkMessageFlag

from . import globals as g
from .core import middleware as mw

EDITED_FORMAT = 'Я всё видела!\n{name} изменил{ending} прикреплённое сообщение.'
DELETED_FORMAT = 'Не надо так!\n{name} удалил{ending} сообщение.'
OLD_TEXT_FORMAT = '\nСтарый текст:\n\n{text}'
ENDINGS = ('(а)', 'а', '')


def format_msg(fmt, msg):
    user = g.store.get_profile(msg['from_id'])
    name = f"{user['first_name']} {user['last_name']}"
    ending = ENDINGS[user['sex']]

    res = fmt.format(name=name, ending=ending)
    if msg['text']:
        # to visually distinguish the quotation
        text = '> ' + msg['text'].replace('\n', '\n> ')
        res += OLD_TEXT_FORMAT.format(text=text)
    return res


@mw.event_type(VkEventType.MESSAGE_NEW)
@mw.cond(lambda m: m.to_me)
def message_new(msg, nxt):
    g.store.update_message(msg)


@mw.event_type(VkEventType.MESSAGE_EDIT)
def message_edited(msg, nxt):
    old = g.store.update_message(msg)
    if old:
        g.bot.send(
            peer_id=msg.peer_id,
            message=format_msg(EDITED_FORMAT, old),
            reply_to=msg.message_id,
        )


@mw.flags_set(VkMessageFlag.DELETED_ALL)
def message_deleted(msg, nxt):
    old = g.store.delete_message(msg.message_id)
    if old:
        g.bot.send(
            peer_id=msg.peer_id,
            message=format_msg(DELETED_FORMAT, old),
        )
