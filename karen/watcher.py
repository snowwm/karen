import logging

from jellyfish import damerau_levenshtein_distance

from karen import ui_strings
from karen.models import Event, EventType

logger = logging.getLogger(__name__)


class Watcher:
    def __init__(self, app) -> None:
        self._app = app

    def setup(self) -> None:
        self._app.use(self.message_new)
        self._app.use(self.message_edited)
        self._app.use(self.message_deleted)

    def message_new(self, event: Event) -> bool:
        if event.type is not EventType.MESSAGE_NEW:
            return False

        logger.debug("%s", event)
        self._app.storage.update_message(event.message)
        return True

    def message_edited(self, event: Event) -> bool:
        if event.type is not EventType.MESSAGE_EDITED:
            return False

        logger.debug("%s", event)
        msg = event.message
        old_msg = self._app.storage.find_message(msg.id)
        self._app.storage.update_message(msg)

        if old_msg and not self._is_minor_edit(old_msg.text or "", msg.text or ""):
            self._notify_users(event, old_msg.text, reply_to=msg.id)

        return True

    def message_deleted(self, event: Event) -> bool:
        if event.type is not EventType.MESSAGE_DELETED:
            return False

        logger.debug("%s", event)
        if old_msg := self._app.storage.find_message(event.message.id):
            self._notify_users(event, old_msg.text)

        return True

    def _notify_users(self, event: Event, old_text: str, reply_to: int = None) -> None:
        user = self._app.api.get_user(event.message.from_id)
        text = ui_strings.message_changed(event.type, user, bool(old_text))
        self._app.api.send_message(
            conversation_id=event.conversation_id,
            text=text,
            reply_to=reply_to,
        )

        if old_text:
            self._app.api.send_message(
                conversation_id=event.conversation_id,
                text=old_text,
            )

    def _is_minor_edit(self, old_text: str, new_text: str) -> bool:
        # Warning: O(len(s1)*len(s2)).
        d = damerau_levenshtein_distance(old_text, new_text)
        logger.debug("%r ~ %r = %d", old_text, new_text, d)
        return d <= 3
