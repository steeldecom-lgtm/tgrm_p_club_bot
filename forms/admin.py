from aiogram.fsm.state import State, StatesGroup

class AdminState(StatesGroup):
    wait_for_rating_data = State()
    wait_for_new_slots = State()   # Ожидание нового количества мест
    wait_for_new_name = State()    # Ожидание нового названия

class CreateTournamentState(StatesGroup):
    wait_for_name = State()
    wait_for_date = State()
    wait_for_time = State()
    wait_for_slots = State()