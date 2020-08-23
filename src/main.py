from pathlib import Path
import logging

from telethon import TelegramClient
import colorlog

from config import CONFIG
from handlers import general


# LOGGING SETUP
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
formatter = colorlog.ColoredFormatter(
    '%(log_color)s%(asctime)s - %(name)s - %(message)s'
)

console = logging.StreamHandler()
console.setLevel(logging.INFO)
console.setFormatter(formatter)

debug_file = logging.FileHandler(Path.cwd().joinpath(CONFIG['LOG']['DEBUG']))
debug_file.setLevel(logging.DEBUG)
debug_file.setFormatter(formatter)

info_file = logging.FileHandler(Path.cwd().joinpath(CONFIG['LOG']['INFO']))
info_file.setLevel(logging.INFO)
info_file.setFormatter(formatter)

err_file = logging.FileHandler(Path.cwd().joinpath(CONFIG['LOG']['ERR']))
err_file.setLevel(logging.WARNING)
err_file.setFormatter(formatter)

[logger.addHandler(handler) for handler in [
    console, debug_file, info_file, err_file
]]


# BOT HANDLER SETUP
client = TelegramClient(
    session=CONFIG['TELETHON']['SESSION'],
    api_id=CONFIG['TELETHON']['ID'],
    api_hash=CONFIG['TELETHON']['HASH']
).start(bot_token=CONFIG['TELETHON']['TOKEN'])

with client:
    # TODO: import and add handlers
    client.add_event_handler(general.master_handler)

    client.run_until_disconnected()
