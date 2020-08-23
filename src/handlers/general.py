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

    logger.warn(f'current: {current_fsm}, future: {future_fsm}')

    tree = {
        "0": {
            "0": fsm_handler,
            "1": fsm_handler
        },
        "1": {
            "1": fsm_handler,
            "2": fsm_handler
        },
        "2": {
            "2": fsm_handler,
            "3": finished_setup_handler
        },
        "3": {
            "3": finished_setup_handler,
            "0": fsm_handler,
            "1": fsm_handler
        }
    }

    await tree[current_fsm][future_fsm](event, user)


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
        future_state_data['payload']
    )

    await method(
        utility.expand_text(
            future_state_data['text'][user.language],
            REPLIES,
            user.language
        ),
        buttons=keyboard,
        parse_mode='HTML'
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

    time = utility.check_time()
    custom_keyboard = [[
        Button.inline(
            REPLIES['MESSAGES']['CUSTOM']['BACK'][user.language],
            '0:dummy_data'
        ),
        Button.url(
            REPLIES['MESSAGES']['CUSTOM']['SHARE'][user.language],
            utility.share_link_gen(
                REPLIES['MESSAGES'][time][user.person_status]
                [user.recruit_status][user.language]
            )
        )
    ]]

    await method(
        REPLIES['MESSAGES'][time][user.person_status]
        [user.recruit_status][user.language],
        buttons=custom_keyboard,
        parse_mode='HTML'
    )

    user.requests += 1
    user.save()
