import time
import copy
import threading
import logging

from wrapt import synchronized

from .. import globals as g

CLEANUP_INTERVAL = 3600  # 1 hour
MESSAGE_TTL = 3600 * 25  # 25 hours

logger = logging.getLogger(__name__)


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
        logger.info('Updating message #%s', msg_id)

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
        logger.info('Deleting message #%s', msg_id)
        return self._msgs.pop(msg_id, None)

    @synchronized
    def get_profile(self, user_id):
        return self._users.get(user_id)

    @synchronized
    def cleanup(self):
        logger.warning('Starting cleanup...')
        logger.warning('Before: %d msgs, %d users',
                       len(self._msgs), len(self._users))

        # clean messages
        now = int(time.time())
        self._msgs = {k: v for k, v in self._msgs.items()
                      if now - v['date'] <= MESSAGE_TTL}

        # clean profiles
        alive_users = {msg['from_id'] for msg in self._msgs.values()}
        self._users = {k: v for k, v in self._users.items()
                       if k in alive_users}

        logger.warning('After: %d msgs, %d users',
                       len(self._msgs), len(self._users))

        # schedule the next iteration
        t = threading.Timer(CLEANUP_INTERVAL, self.cleanup)
        t.daemon = True
        t.start()

    # No sync, since it's a private method already called with a lock
    def _fetch_message(self, msg_id):
        res = g.bot.get_messages(message_ids=msg_id, extended=1, fields='sex')

        if not res['count']:
            logger.warning('Empty fetch response for msg #%s', msg_id)
        else:
            msg = res['items'][0]
            from_id = msg['from_id']

            # ignore own messages
            if msg['out']:
                logger.debug('Ignoring message #%s from self', msg['id'])
                return None

            # ignore special chat actions
            if 'action' in msg:
                logger.debug('Ignoring action %s', msg['action'])
                return None

            # I don't talk to groups, ever
            # God knows what could happen if two bots felt like wagging their tongues together
            if from_id < 0:
                logger.debug('Ignoring message from group %s', from_id)
                return None

            # ensure we have user data
            if 'profiles' in res:
                users = [x for x in res['profiles'] if x['id'] == from_id]
                if users and users[0]:
                    logger.info('Updating user %s', from_id)
                    self._users[from_id] = users[0]
                    return msg

            logger.warning('User profile #%s not fetched', from_id)
            return None
