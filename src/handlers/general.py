import logging
from typing import Union
from telethon import events, Button

from process.database import User, user_decorator
from process import utility
from config import REPLIES


logger = logging.getLogger(__name__)


@events.register(events.CallbackQuery())
@events.register(events.NewMessage())
@user_decorator(increment=False)
async def master_handler(
    event: Union[events.CallbackQuery.Event, events.NewMessage.Event],
    user: User
):
    if hasattr(event, 'query'):
        future_fsm, _ = event.data.decode('utf-8').split(':')
    else:
        future_fsm = user.fsm_state

    current_fsm = user.fsm_state

    tree = {
        "0": {
            "0": fsm_handler,
            "1": fsm_handler
        },
        "1": {
            "0": fsm_handler,
            "1": fsm_handler,
            "2": fsm_handler
        },
        "2": {
            "0": fsm_handler,
            "1": fsm_handler,
            "2": fsm_handler,
            "3": finished_setup_handler
        },
        "3": {
            "3": finished_setup_handler,
            "2": fsm_handler
        }
    }
    try:
        await tree[current_fsm][future_fsm](event, user)
    except KeyError:
        await event.edit(
            REPLIES['DISPLAY']['CUSTOM']['REMOVED'][user.language]
        )


async def fsm_handler(
    event: Union[events.CallbackQuery.Event, events.NewMessage.Event],
    user: User
):
    # if it's a callback
    if hasattr(event, 'query'):
        method = event.edit  # edit the original message
        future_fsm, db_data = event.data.decode('utf-8').split(':')
        user.fsm_state = future_fsm
        user.set_from_string(db_data)
    else:
        method = event.respond  # respond to the original message
        future_fsm = user.fsm_state

    future_state_data = REPLIES['FSM'][future_fsm]

    keyboard = utility.keyboard_gen(
        future_state_data['markup'],
        future_state_data['payload'],
        language=user.language
    )

    await method(
        utility.expand_text(
            future_state_data['text'][user.language],
            REPLIES,
            user.language
        ),
        buttons=keyboard,
        parse_mode='Markdown'
    )

    user.requests += 1
    user.save()


async def finished_setup_handler(
    event: Union[events.CallbackQuery.Event, events.NewMessage.Event],
    user: User
):
    # if it's a callback
    if hasattr(event, 'query'):
        method = event.edit
        future_fsm, db_data = event.data.decode('utf-8').split(':')
        user.fsm_state = future_fsm
        user.set_from_string(db_data)
    else:
        method = event.respond

    custom_keyboard = [[
        Button.inline(
            REPLIES['DISPLAY']['CUSTOM']['BACK'][user.language],
            '2:dummy_data'
        )
    ]]

    await method(
        REPLIES['DISPLAY']['MESSAGES'][user.labor_status]
        [user.recruit_status][user.language],
        buttons=custom_keyboard,
        parse_mode='Markdown',
        link_preview=True
    )

    user.requests += 1
    user.save()
