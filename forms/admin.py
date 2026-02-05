from aiogram.fsm.state import State, StatesGroup

class AdminState(StatesGroup):
    wait_for_rating_data = State() #ожидание ника и баллов