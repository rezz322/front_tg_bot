from aiogram import Router, types
from aiogram.filters import CommandStart
from api_user import user_api as backend_api
from keyboards import get_admin_main_menu, get_user_main_menu, get_unauthorized_keyboard

router = Router()

@router.message(CommandStart())
async def cmd_start(message: types.Message):
    user_data = {
        "id": str(message.from_user.id),
        "username": message.from_user.username or "unknown"
    }
    
    # Try to register user on backend
    await backend_api.register_user(user_data)
    
    # Check if user is admin via backend API
    admin_response = await backend_api.check_admin(message.from_user.id)
    is_admin = admin_response.get("isAdmin", False) if isinstance(admin_response, dict) else False
    if is_admin:
        await message.answer(
            f"Привіт, Адмін {message.from_user.first_name}! (Права адміністратора підтверджено) Оберіть дію:",
            reply_markup=get_admin_main_menu()
        )
    else:
        user_info = await backend_api.get_user_by_id(message.from_user.id)
        print(user_info)
        is_whitelisted = user_info.get("isWhitelisted", False) if isinstance(user_info, dict) else False
        
        if is_whitelisted:
            await message.answer(
                f"Привіт, {message.from_user.first_name}! Оберіть дію:",
                reply_markup=get_user_main_menu()
            )
        else:
            await message.answer(
                f"Привіт, {message.from_user.first_name}! Ви не у білому списку. Доступні обмежені функції:",
                reply_markup=get_unauthorized_keyboard()
            )

@router.message(lambda message: message.text == "⬅️ Back")
async def back_to_main(message: types.Message):
    admin_response = await backend_api.check_admin(message.from_user.id)
    is_admin = admin_response.get("isAdmin", False) if isinstance(admin_response, dict) else False
    
    if is_admin:
        await message.answer("Головне меню:", reply_markup=get_admin_main_menu())
    else:
        user_info = await backend_api.get_user_by_id(message.from_user.id)
        is_whitelisted = user_info.get("isWhitelisted", False) if isinstance(user_info, dict) else False
        
        if is_whitelisted:
            await message.answer("Головне меню:", reply_markup=get_user_main_menu())
        else:
            await message.answer("Вертаємось:", reply_markup=get_unauthorized_keyboard())
