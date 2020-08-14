import logging
from telethon import events

from process.database import User, user_decorator
from config import REPLIES


@events.register(events.NewMessage(pattern='/start'))
async def cmd_start(event):
    pass


@events.register(events.NewMessage(pattern='/help'))
@user_decorator
async def cmd_help(event, user):
    pass
