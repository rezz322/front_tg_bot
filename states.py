from aiogram.fsm.state import State, StatesGroup

class AdminStates(StatesGroup):
    waiting_for_user_id = State()
    waiting_for_account_number = State()
    waiting_for_give_key_user = State()
    waiting_for_give_key_number = State()
    waiting_for_whitelist_username = State()
    waiting_for_give_key_days = State()
    waiting_for_give_key_type = State() # ID or Username
    waiting_for_give_key_username = State()
    
    # Edit Acc States
    waiting_for_edit_acc_field = State()
    waiting_for_edit_acc_value = State()
    waiting_for_user_limit = State()

class BindStates(StatesGroup):
    waiting_for_phone = State()
    waiting_for_pin = State()
