from karen.models import User, UserSex, EventType

_edit_fmt = """\
Я всё видела!
{name} изменил{ending} сообщение."""
_delete_fmt = """\
Как не стыдно!
{name} удалил{ending} сообщение."""
_old_text_fmt = "\nСтарый текст:"

_type_to_format = {
    EventType.MESSAGE_EDITED: _edit_fmt,
    EventType.MESSAGE_DELETED: _delete_fmt,
}

_sex_to_ending = {
    UserSex.UNKNOWN: '(а)',
    UserSex.MALE: '',
    UserSex.FEMALE: 'а',
}

def message_changed(event_type: EventType, user: User, have_old_text: bool) -> str:
    msg = _type_to_format[event_type].format(
        name=f"{user.first_name} {user.last_name}",
        ending=_sex_to_ending[user.sex],
    )
    if have_old_text:
        msg += _old_text_fmt
    return msg
