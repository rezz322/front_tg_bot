import html
from aiogram import Router, types, F
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from api_admin import admin_api as backend_api
from states import AdminStates
from handlers.admin_common import admin_only

router = Router()

@router.message(F.text == "👤 Info User")
@admin_only
async def ask_user_username(message: types.Message, state: FSMContext):
    await message.answer("Введіть Username користувача (без @):")
    await state.set_state(AdminStates.waiting_for_user_id)

@router.message(AdminStates.waiting_for_user_id)
@admin_only
async def process_user_info(message: types.Message, state: FSMContext):
    user_info = await backend_api.get_user_info_by_username(message.text.replace("@", ""), admin_id=message.from_user.id)
    await state.clear()
    
    if "error" in user_info:
        if user_info.get("status") == 404:
            await message.answer("❌ Користувача не знайдено.")
        elif user_info.get("status") == 403:
            await message.answer("🚫 Доступ заборонено.")
        else:
            await message.answer("❌ Помилка при отриманні даних користувача.")
        return
    
    username = html.escape(str(user_info.get('username', 'N/A')))
    is_banned = user_info.get('isBanned', False)
    is_whitelisted = user_info.get('isWhitelisted', False)
    
    response = (
        f"👤 Користувач: <b>{username}</b>\n"
        f"🆔 DB ID: <code>{user_info.get('id')}</code>\n"
        f"📱 TG ID: <code>{user_info.get('telegramId')}</code>\n"
        f"🚫 Бан: {'Так' if is_banned else 'Ні'}\n"
        f"📝 Вайтліст: {'Так' if is_whitelisted else 'Ні'}"
    )
    
    tg_id = user_info.get('telegramId') or user_info.get('id')
    kb_buttons = []
    
    # Ban/Unban row
    kb_buttons.append([
        InlineKeyboardButton(text="✅ Unban" if is_banned else "🚫 Ban", 
                             callback_data=f"{'unban' if is_banned else 'ban'}_{tg_id}")
    ])
    
    # Whitelist row
    wl_user_id = user_info.get('username') or tg_id
    kb_buttons.append([
        InlineKeyboardButton(text="❌ Rem WL" if is_whitelisted else "📝 Add WL", 
                             callback_data=f"{'wlrem' if is_whitelisted else 'wladd'}_{wl_user_id}")
    ])
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=kb_buttons)
    await message.answer(response, parse_mode="HTML", reply_markup=keyboard)

@router.callback_query(F.data.startswith("ban_"))
@admin_only
async def cb_ban_user(callback: types.CallbackQuery):
    user_id = callback.data.split("_")[1]
    result = await backend_api.toggle_user_ban(user_id, admin_id=callback.from_user.id)
    if "error" not in result:
        is_banned = result.get("isBanned", True)
        status_text = "заблокований" if is_banned else "розблокований"
        await callback.message.answer(f"✅ Статус користувача <code>{user_id}</code> змінено: <b>{status_text}</b>.", parse_mode="HTML")
        await callback.answer()

@router.callback_query(F.data.startswith("unban_"))
@admin_only
async def cb_unban_user(callback: types.CallbackQuery):
    user_id = callback.data.split("_")[1]
    result = await backend_api.toggle_user_ban(user_id, admin_id=callback.from_user.id)
    if "error" not in result:
        is_banned = result.get("isBanned", False)
        status_text = "заблокований" if is_banned else "розблокований"
        await callback.message.answer(f"✅ Статус користувача <code>{user_id}</code> змінено: <b>{status_text}</b>.", parse_mode="HTML")
        await callback.answer()

@router.message(F.text == "📝 Whitelist")
@admin_only
async def ask_whitelist_username(message: types.Message, state: FSMContext):
    await message.answer("Введіть Username користувача (без @) для перемикання вайтліста:")
    await state.set_state(AdminStates.waiting_for_whitelist_username)

@router.message(AdminStates.waiting_for_whitelist_username)
@admin_only
async def process_whitelist_username(message: types.Message, state: FSMContext):
    username = message.text.replace("@", "")
    result = await backend_api.toggle_whitelist_by_username(username, admin_id=message.from_user.id)
    await state.clear()
    
    if "error" in result:
        if result.get("status") == 404:
            await message.answer("❌ Користувача не знайдено.")
        else:
            await message.answer("❌ Помилка при зміні статусу вайтліста.")
    else:
        status = "доданий до" if result.get("isWhitelisted") else "видалений з"
        await message.answer(f"✅ Користувач @{username} {status} вайтліста.")

@router.callback_query(F.data.startswith("wladd_") | F.data.startswith("wlrem_"))
@admin_only
async def cb_toggle_whitelist(callback: types.CallbackQuery):
    parts = callback.data.split("_")
    target = parts[1]
    
    if target.isdigit():
        result = await backend_api.toggle_whitelist(target, admin_id=callback.from_user.id)
    else:
        result = await backend_api.toggle_whitelist_by_username(target, admin_id=callback.from_user.id)
    
    if "error" not in result:
        status = "доданий до" if result.get("isWhitelisted") else "видалений з"
        await callback.message.answer(f"✅ Користувач <code>{target}</code> {status} вайтліста.", parse_mode="HTML")
        await callback.answer()

@router.message(F.text == "👥 All Users")
@admin_only
async def list_all_users(message: types.Message):
    users = await backend_api.list_users(message.from_user.id)
    
    if "error" in users:
        await message.answer("❌ Помилка при отриманні списку користувачів.")
        return
    
    if not users:
        await message.answer("📭 Користувачі відсутні.")
        return
    
    text = "👥 <b>Зареєстровані користувачі:</b>\n"
    for user in users:
        ban_status = "🚫 Забанений" if user.get('isBanned') else "✅ Активний"
        wl_status = "📝 WL" if user.get('isWhitelisted') else "❌ No WL"
        admin_status = "⭐ Адмін" if user.get('isAdmin') else "👤 Юзер"
        tg_id = user.get('telegramId') or user.get('id')
        username = html.escape(str(user.get('username', 'unknown')))
        text += f"\n{admin_status} | <b>{username}</b>\n   TG: <code>{tg_id}</code> | {ban_status} | {wl_status}\n"
    
    await message.answer(text, parse_mode="HTML")
