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

    if hasattr(event, 'query') and current_state_data['edit']:
        method = event.edit  # edit the original message
        future_fsm, db_data = event.data.decode('utf-8').split(':')
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
