# TODO: add commands + some kind of help
# TODO: add admin notifications
# TODO: add laconic mode, love4love mode
# TODO: forgive typos
# TODO: think about persistence
# FIXME: comment the code (an everlasting problem)

import logging
from logging import config as logging_config
import os
from typing import Any, Callable

from karen.api import Api
from karen.models import Event
from karen.storage import Storage
from karen.watcher import Watcher

logger = logging.getLogger(__name__)


class App:
    storage: Storage
    config: dict[str, Any]
    api: Api
    _handlers: list

    def __init__(self) -> None:
        logging.basicConfig(style="{", format="{levelname:3.3} {name}: {message}")

        self.storage = Storage(os.environ.get("KAREN_DB_URL"))
        self.config = self.storage.get_config()
        if "logging" in self.config:
            logging_config.dictConfig(self.config["logging"])

        self._handlers = []
        Watcher(self).setup()

        self.api = Api(self, self.config["access_token"])
        logger.info("Starting bot")
        self.api.poll()

    def use(self, *handlers: Callable[[Event], bool]) -> None:
        """Handlers are executed for each event in the order they were added
        until one returns a truthy value.
        """
        self._handlers.extend(handlers)

    def handle(self, event: Event) -> None:
        try:
            for h in self._handlers:
                if h(event):
                    break
        except Exception:
            logger.exception("In handlers:")
