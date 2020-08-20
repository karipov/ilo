import logging
from typing import Union
from telethon import events

from process.database import User, user_decorator
from process import utility
from config import REPLIES


logger = logging.getLogger(__name__)


@events.register(events.CallbackQuery())
@events.register(events.NewMessage())
@user_decorator(increment=False)
async def fsm_handler(
    event: Union[events.CallbackQuery.Event, events.NewMessage.Event],
    user: User
):
    if not utility.check_fsm(user):
        return

    current_state_data = REPLIES['FSM'][user.fsm_state]

    # if it's a callback
    if hasattr(event, 'query'):
        method = event.edit  # edit the original message
        future_fsm, db_data = event.data.decode('utf-8').split(':')
        user.fsm_state = future_fsm
        user.set_from_string(db_data)
    else:
        method = event.respond  # respond to the original message
        future_fsm = user.fsm_state

    if current_state_data.get('terminal'):
        return

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


@events.register(events.CallbackQuery())
@events.register(events.NewMessage())
@user_decorator(increment=False)
async def finished_setup_handler(
    event: Union[events.CallbackQuery.Event, events.NewMessage.Event],
    user: User
):
    if not user.fsm_state == 'done':
        return

    # if it's a callback
    if hasattr(event, 'query'):
        method = event.edit
    else:
        method = event.respond

    time = utility.check_time()

    await method(
        REPLIES['MESSAGES'][time][user.person_status]
        [user.recruit_status][user.language],
        parse_mode='HTML'
    )
