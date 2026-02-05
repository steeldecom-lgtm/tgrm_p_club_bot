from aiogram.fsm.state import State, StatesGroup

class Form(StatesGroup):
    name = State()
    nickname = State()
    level = State()