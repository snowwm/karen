import logging

from karen import ui_strings
from karen.models import Event, EventType

logger = logging.getLogger(__name__)


class Watcher:
    def __init__(self, app) -> None:
        self._app = app

    def setup(self) -> None:
        self._app.use(self.message_new)
        self._app.use(self.message_changed)

    def message_new(self, event: Event) -> bool:
        if event.type is not EventType.MESSAGE_NEW:
            return False

        logger.debug("%s", event)
        self._app.storage.update_message(event.message)
        return True

    def message_changed(self, event: Event) -> bool:
        if event.type not in (EventType.MESSAGE_EDITED, EventType.MESSAGE_DELETED):
            return False

        logger.debug("%s", event)
        msg = event.message
        is_edited = event.type is EventType.MESSAGE_EDITED
        old_msg = self._app.storage.find_message(msg.id)

        if is_edited:
            self._app.storage.update_message(msg)

        if old_msg:
            have_old_text = bool(old_msg.text)
            user = self._app.api.get_user(msg.from_id)
            text = ui_strings.message_changed(event.type, user, have_old_text)
            self._app.api.send_message(
                conversation_id=event.conversation_id,
                text=text,
                reply_to=msg.id if is_edited else None,
            )

            if have_old_text:
                self._app.api.send_message(
                    conversation_id=event.conversation_id,
                    text=old_msg.text,
                )

        return True
