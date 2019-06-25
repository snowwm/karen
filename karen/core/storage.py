import time
import copy
import threading

from wrapt import synchronized

from .. import globals as g

CLEANUP_INTERVAL = 3600  # 1 hour
MESSAGE_TTL = 3600 * 25  # 25 hours


class Storage:
    def __init__(self):
        self._msgs = {}
        self._users = {}
        self.cleanup()

    @synchronized
    def get_message(self, msg_id):
        return self._msgs.get(msg_id)

    @synchronized
    def update_message(self, msg):
        msg_id = msg.message_id
        old = self._msgs.get(msg_id)

        if old:
            new = copy.deepcopy(old)
            new['date'] = msg.timestamp
            new['text'] = msg.text
            # that's enough for now
        else:
            new = self._fetch_message(msg_id)

        if new:
            self._msgs[msg_id] = new

        return old

    @synchronized
    def delete_message(self, msg_id):
        return self._msgs.pop(msg_id, None)

    @synchronized
    def get_profile(self, user_id):
        return self._users.get(user_id)

    @synchronized
    def cleanup(self):
        # clean messages
        now = int(time.time())
        self._msgs = {k: v for k, v in self._msgs.items()
                      if now - v['date'] <= MESSAGE_TTL}

        # clean profiles
        alive_users = {msg['from_id'] for msg in self._msgs.values()}
        self._users = {k: v for k, v in self._users.items()
                       if k in alive_users}

        # schedule the next iteration
        t = threading.Timer(CLEANUP_INTERVAL, self.cleanup)
        t.daemon = True
        t.start()

    # No sync, since it's a private method already called with a lock
    def _fetch_message(self, msg_id):
        res = g.bot.get_messages(message_ids=msg_id, extended=1, fields='sex')
        print(res)

        if res['count']:
            msg = res['items'][0]
            from_id = msg['from_id']

            # ignore special chat actions
            if 'action' in msg:
                return None

            # I don't talk to groups, ever
            # God knows what could happen if two bots felt like wagging their tongues together
            if from_id < 0:
                return None

            user = res['profiles'][0]
            self._users[from_id] = user
            return msg
