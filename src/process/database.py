from pathlib import Path
from typing import Callable, Any
import logging
import functools

from peewee import Model, SqliteDatabase
from peewee import CharField, IntegerField, BooleanField

from config import CONFIG


logger = logging.getLogger(__name__)
db = SqliteDatabase(Path.cwd().joinpath(CONFIG['LOG']['DB']))


class User(Model):
    user_id = IntegerField(primary_key=True)
    language = CharField(default='none')
    # find yourself / recruiters recruit / voluntary workers status
    recruit_status = CharField(default='none')
    labor_status = CharField(default='none')

    fsm_state = CharField(default='0')
    requests = IntegerField(default=0)
    is_ban = BooleanField(default=False)

    class Meta:
        database = db

    def set_from_string(self, string: str, save: bool = False):
        if '->' not in string:
            return

        attr, value = string.split('->')

        if hasattr(self, attr):
            setattr(self, attr, value)
        else:
            raise AttributeError(f"{self} object has no attribute {attr}")

        if save:
            self.save()


def user_decorator(increment: bool = True):

    def user_getter(func: Callable[..., Any]):
        """
        Decorator for get_or_create and requests incrementing
        """
        functools.wraps(func)

        async def func_wrapper(event, *args, **kwargs):
            user, _ = User.get_or_create(
                user_id=event.chat_id,
                defaults={'language': 'en'}
            )

            await func(event, user, *args, **kwargs)

            if increment:
                user.requests += 1

            user.save()

        return func_wrapper
    return user_getter


db.connect()
db.create_tables([User])
logger.info("SQLite database connected, tables created")
