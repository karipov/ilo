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
    logger.warn(f"current state: {user.fsm_state}")

    if user.fsm_state in ['0', '1']:
        await fsm_handler(event, user)
    elif user.fsm_state in ['2', '3']:
        await finished_setup_handler(event, user)
    else:
        logger.error('User {user.user_id} is out of predefined FSM states')
        return


async def fsm_handler(
    event: Union[events.CallbackQuery.Event, events.NewMessage.Event],
    user: User
):
    # if it's a callback
    if hasattr(event, 'query'):
        method = event.edit  # edit the original message
        future_fsm, db_data = event.data.decode('utf-8').split(':')
        logging.warn(f'fsm_handler future fsm {future_fsm}')
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

        # if we're returning back, offload to fsm_handler
        if user.fsm_state == '1':
            await fsm_handler(event, user)
            return

        user.set_from_string(db_data)
    else:
        method = event.respond

    time = utility.check_time()
    custom_keyboard = [[
        Button.inline(
            REPLIES['MESSAGES']['CUSTOM']['BACK'][user.language],
            '1:dummy_data'
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
