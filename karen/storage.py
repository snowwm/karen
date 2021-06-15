from typing import Optional, Any

from pymongo import MongoClient

from karen.models import Message


class Storage:
    def __init__(self, db_url: str) -> None:
        self._db = MongoClient(db_url).get_default_database()
        self._msgs = self._db.get_collection("messages")

    def get_config(self) -> dict[str, Any]:
        return self._db.get_collection("singletons").find_one({"_id": "config"}) or {}

    def find_message(self, msg_id: int) -> Optional[Message]:
        if raw := self._msgs.find_one({"_id": msg_id}):
            raw["id"] = raw.pop("_id")
            return Message.from_dict(raw)

    def update_message(self, msg: Message) -> None:
        raw = msg.as_dict()
        raw["_id"] = raw.pop("id")
        self._msgs.update_one({"_id": msg.id}, {"$set": raw}, upsert=True)
