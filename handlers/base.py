from aiogram import Router, types
from aiogram.filters import CommandStart
from api_user import user_api as backend_api
from keyboards import get_admin_main_menu, get_user_main_menu, get_unauthorized_keyboard

router = Router()

@router.message(CommandStart())
async def cmd_start(message: types.Message):
    # Perform a single check for both access and admin status
    # This also handles auto-registration on the backend
    access_data = await backend_api.check_access(message.from_user.id, username=message.from_user.username)
    
    if not isinstance(access_data, dict):
        await message.answer("❌ Помилка при перевірці доступу. Спробуйте пізніше.")
        return

    is_admin = access_data.get("isAdmin", False)
    allowed = access_data.get("allowed", False)
    status_msg = access_data.get("message", "Доступ заборонено.")

    if is_admin:
        await message.answer(
            f"Привіт, Адмін {message.from_user.first_name}! Оберіть дію:",
            reply_markup=get_admin_main_menu()
        )
        return

    if allowed:
        await message.answer(
            f"Привіт, {message.from_user.first_name}! {status_msg} Оберіть дію:",
            reply_markup=get_user_main_menu()
        )
    else:
        await message.answer(
            f"🚫 {status_msg}",
            reply_markup=get_unauthorized_keyboard()
        )

@router.message(lambda message: message.text == "⬅️ Назад")
async def back_to_main(message: types.Message):
    access_data = await backend_api.check_access(message.from_user.id, username=message.from_user.username)
    
    if not isinstance(access_data, dict):
        await message.answer("Вертаємось:", reply_markup=get_unauthorized_keyboard())
        return

    if access_data.get("isAdmin", False):
        await message.answer("Головне меню:", reply_markup=get_admin_main_menu())
    elif access_data.get("allowed", False):
        await message.answer("Головне меню:", reply_markup=get_user_main_menu())
    else:
        await message.answer("Вертаємось:", reply_markup=get_unauthorized_keyboard())
