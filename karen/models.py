from datetime import datetime
from enum import Enum
from typing import Optional

from karen.util import MyDataclass


class Message(MyDataclass):
    id: int
    from_id: Optional[int]
    updated_at: Optional[datetime]
    text: Optional[str]


class EventType(Enum):
    MESSAGE_NEW = 0
    MESSAGE_EDITED = 1
    MESSAGE_DELETED = 2


class Event(MyDataclass):
    type: EventType
    conversation_id: int
    message: Message


class UserSex(Enum):
    UNKNOWN = 0
    FEMALE = 1
    MALE = 2


class User(MyDataclass):
    id: int
    first_name: str
    last_name: str
    sex: UserSex
