from aiogram.dispatcher.filters.state import StatesGroup, State


class WorkUAState(StatesGroup):
    WaitingForInput = State()
    Categories = State()
    Pages = State()
