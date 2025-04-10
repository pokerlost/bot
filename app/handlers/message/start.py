from __future__ import annotations

from aiogram import Router
from aiogram.filters import CommandStart, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state
from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
    SwitchInlineQueryChosenChat,
)
from aiogram.utils.formatting import Bold
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from pokerengine.engine import EngineRake01
from pokerengine.pretty_string import PrettyCard
from redis.asyncio import Redis

from core.poker.core import poker_chat_job
from core.poker.schema import Poker
from filters import PokerFilter
from metadata import BB_BET, BB_MULT
from states import States
from utils.id import get_player_id
from utils.inline_query import get_id

router = Router()


@router.message(
    CommandStart(deep_link=True),
    StateFilter(default_state),
    PokerFilter(),
)
async def start_deep_link_handler(
    message: Message,
    state: FSMContext,
    poker: Poker,
    engine: EngineRake01,
    redis: Redis,
    scheduler: AsyncIOScheduler,
    pretty_card: PrettyCard,
) -> None:
    new_message = await message.answer(
        **Bold("Poker created. Wait until game starts.").as_kwargs()
    )

    await state.update_data(poker=poker.id)
    await state.set_state(state=States.LOADING)
    scheduler.add_job(
        poker_chat_job,
        kwargs={
            "bot": message.bot,
            "player": engine.add_player(
                stack=BB_BET * BB_MULT,
                id=get_player_id(user=message.from_user),
                parameters={
                    "chat_id": new_message.chat.id,
                    "message_id": new_message.message_id,
                },
            ),
            "poker": poker,
            "state": state,
            "redis": redis,
            "pretty_card": pretty_card,
        },
        trigger="interval",
        id=get_id(),
        max_instances=1,
        seconds=1,
    )


@router.message(CommandStart(deep_link=False), PokerFilter())
async def start_handler(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer(
        **Bold("Welcome to Poker!").as_kwargs(),
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="Create",
                        switch_inline_query_chosen_chat=SwitchInlineQueryChosenChat(
                            query="create",
                            allow_user_chats=True,
                            allow_bot_chats=False,
                            allow_group_chats=True,
                            allow_channel_chats=False,
                        ),
                    )
                ]
            ],
        ),
    )
