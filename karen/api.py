import logging
from typing import Callable, Optional

from requests.exceptions import ReadTimeout
from vk_api import utils
from vk_api.longpoll import Event as VkEvent
from vk_api.longpoll import VkEventType, VkLongPoll, VkMessageFlag
from vk_api.vk_api import VkApi

from karen.models import Event, EventType, Message, User, UserSex

logger = logging.getLogger(__name__)


class Api:
    def __init__(self, token: str) -> None:
        self._vk = VkApi(token=token)
        self._api = self._vk.get_api()

    def poll(self, handler: Callable[[Event], None]) -> None:
        poll = VkLongPoll(self._vk)
        while True:
            try:
                events = poll.check()
            except ReadTimeout:
                logger.warning("Poll read timeout")
                continue

            for event in events:
                logger.debug("Received raw event: %s", event.raw)
                if event := self._create_event(event):
                    handler(event)

    def _create_event(self, obj: VkEvent) -> Optional[Event]:
        """Returns None for events we definitely don't care for."""

        # Note: `from_me` will be always false on MESSAGE_EDITED events
        # - just assume we never edit our messages.
        if obj.from_me:
            return None

        if obj.type is VkEventType.MESSAGE_NEW:
            ev_type = EventType.MESSAGE_NEW
        elif obj.type is VkEventType.MESSAGE_EDIT:
            ev_type = EventType.MESSAGE_EDITED
        elif (
            obj.type is VkEventType.MESSAGE_FLAGS_REPLACE
            and obj.flags & VkMessageFlag.DELETED_ALL
        ) or (
            obj.type is VkEventType.MESSAGE_FLAGS_SET
            and obj.mask & VkMessageFlag.DELETED_ALL
        ):
            ev_type = EventType.MESSAGE_DELETED
        else:
            return None

        msg = Message(
            id=obj.message_id,
            from_id=getattr(obj, "user_id", None),
            updated_at=getattr(obj, "datetime", None),
            text=getattr(obj, "message", None),
        )
        return Event(ev_type, obj.peer_id, msg)

    def send_message(self, conversation_id: int, text: str, **kwargs) -> None:
        kwargs["peer_id"] = conversation_id
        kwargs["message"] = text
        kwargs.setdefault("random_id", utils.get_random_id())
        self._api.messages.send(**kwargs)

    def get_user(self, user_id: int) -> Optional[User]:
        res = self._api.users.get(user_ids=user_id, fields="sex")
        if res:
            obj = res[0]
            return User(
                id=obj["id"],
                first_name=obj["first_name"],
                last_name=obj["last_name"],
                sex=UserSex(obj["sex"]),
            )
        return None
