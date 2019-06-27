from vk_api.longpoll import VkEventType


class MiddlewareContainer:
    def __init__(self):
        self._mw = []

    def use(self, *funcs):
        self._mw.extend(funcs)

    def run_middleware(self, ctx):
        last_index = -1

        def exec(i):
            nonlocal last_index
            if i <= last_index:
                raise RuntimeError('next() called multiple times')
            last_index = i
            if i == len(self._mw):
                return None
            return self._mw[i](ctx, lambda: exec(i + 1))

        return exec(0)


def cond(pred):
    return lambda func: lambda ctx, next: func(ctx, next) if pred(ctx) else next()
    # OMG.


def event_type(*types):
    return cond(lambda event: event.type in types)


def flags_set(*flags, combine=all):
    def test(event):
        if event.type is VkEventType.MESSAGE_FLAGS_REPLACE:
            have = event.flags
        elif event.type is VkEventType.MESSAGE_FLAGS_SET:
            have = event.mask
        else:
            return False

        return combine((f & have for f in flags))

    return cond(test)
