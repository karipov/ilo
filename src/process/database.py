from pathlib import Path
import logging

from peewee import Model, SqliteDatabase
from peewee import CharField, IntegerField, BooleanField


class User(Model):
    user_id = IntegerField(primary_key=True)
    language = CharField(default='none')
    requests = IntegerField(default=0)
    is_ban = BooleanField(default=False)

    class Meta:
        database = db


def user_decorator(func):
    """
    Decorator for get_or_create and requests incrementing
    """
    async def func_wrapper(event, *args, **kwargs):
        user, _ = User.get_or_create(
            user_id=event.from_id,
            defaults={'language': 'en'}
        )

        await func(event, user, *args, **kwargs)

        user.requests += 1
        user.save()
        

    return func_wrapper



logger = logging.getLogger(__name__)
db = SqliteDatabase(Path.cwd().joinpath('src/logs/users.db'))
db.connect()
db.create_tables([User])
logger.info("SQLite database connected, tables created")