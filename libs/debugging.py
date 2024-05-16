from functools import wraps, partial
from datetime import datetime
from libs.loggingFuncs import print_and_log
from libs.loggingFuncs import setup_logger
from config.constant import PATH_RESULT
import os


logger = setup_logger('aa', os.path.join(PATH_RESULT, f"log_{'{:%Y_%m_%d_%H_%M_%S}'.format(datetime.utcnow())}.txt"))


"""
handle_static - False if static should be skipped
prefix - before msg
suffix - after msg
"""


def debugmethods(cls=None, *, logger=logger, prefix='', handle_static=True, suffix=''):
    if cls is None:
        return partial(debugmethods, logger=logger, prefix=prefix, handle_static=handle_static, suffix=suffix)

    for name in (name for name in dir(cls) if (callable(getattr(cls, name)) and (
            not (name.startswith('__') and name.endswith('__'))))):
        method = getattr(cls, name)
        obj = cls.__dict__[name] if name in cls.__dict__ else method
        if isinstance(obj, staticmethod):
            if handle_static:
                kind = 'static method'
            else:
                kind = 'skip_static'
        elif isinstance(obj, classmethod):
            kind = 'class method'
        else:
            kind = 'method'
        setattr(cls, name, wrapping(method, kind=kind, logger=logger, prefix=prefix, suffix=suffix))
    return cls


def wrapping(method=None, *, kind='method', logger=logger, prefix='', suffix=''):
    if method is None:
        return partial(wrapping, logger=logger, prefix=prefix, kind=kind, suffix=suffix)
    msg = prefix + method.__qualname__

    if kind == 'static method':
        @staticmethod
        def wrapped(*args, **kwargs):
            return _wrapped(*args, **kwargs)
    elif kind == 'skip_static':
        @staticmethod
        def wrapped(*args, **kwargs):
            return _not_wrapped(*args, **kwargs)
    elif kind == 'class method':
        @classmethod
        def wrapped(cls, *args, **kwargs):
            return _wrapped(*args, **kwargs)
    elif kind == 'not_class':
        def wrapped(*args, **kwargs):
            return _wrapped(*args, **kwargs)
    else:
        def wrapped(self, *args, **kwargs):
            return _wrapped(self, *args, **kwargs)

    @wraps(method)
    def _wrapped(*args, **kwargs):
        print_and_log(logger, f'{msg}{suffix}')
        return method(*args, **kwargs)

    def _not_wrapped(*args, **kwargs):
        return method(*args, **kwargs)

    return wrapped
