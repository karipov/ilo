import loging
from telethon import events

from process.database import User, user_decorator
from config import REPLIES


@events.register(events.NewMessage(pattern='/start'))
async def start(event):
    pass


@events.register(events.NewMessage(pattern='/help'))
@user_decorator
async def help(event, user):
    pass
