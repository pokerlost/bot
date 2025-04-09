from __future__ import annotations

from aiogram.filters.callback_data import CallbackData


class SelectActionCallbackData(CallbackData, prefix="select_action"):
    action: int
    position: int
    amount: int
