import html
import logging
from aiogram import Router, types, F
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from api_admin import admin_api as backend_api
from api_user import user_api
from states import AdminStates
from handlers.admin_common import admin_only
from utils.formatters import format_user_info
from utils.keyboards import get_confirm_keyboard

router = Router()

@router.message(F.text == "👤 Інфо Користувача")
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
    
    response = format_user_info(user_info)
    tg_id = user_info.get('telegramId') or user_info.get('id')
    is_banned = user_info.get('isBanned', False)
    is_whitelisted = user_info.get('isWhitelisted', False)
    
    kb_buttons = []
    
    # Ban/Unban & Whitelist buttons
    kb_buttons.append([
        InlineKeyboardButton(text="✅ Розбанити" if is_banned else "🚫 Забанити", 
                             callback_data=f"{'unban' if is_banned else 'ban'}_{tg_id}"),
        InlineKeyboardButton(text="❌ Вид WL" if is_whitelisted else "📝 Дод WL", 
                             callback_data=f"{'wlrem' if is_whitelisted else 'wladd'}_{user_info.get('username') or tg_id}")
    ])
    
    # User's accounts removal buttons
    logging.info(f"Fetching accounts for tg_id: {tg_id}")
    try:
        accounts = await backend_api.get_user_accounts(tg_id, admin_id=message.from_user.id)
        logging.info(f"Accounts result: {accounts}")
        
        if isinstance(accounts, list) and accounts:
            response += "\n\n🔑 <b>Акаунти користувача:</b>"
            has_active = False
            for acc in accounts:
                if acc.get('isBanned'): 
                    continue
                has_active = True
                phone = acc.get('phone', 'N/A')
                response += f"\n- <code>{phone}</code>"
                kb_buttons.append([
                    InlineKeyboardButton(text=f"❌ Видалити {phone}", 
                                         callback_data=f"rmacc_{phone}_{tg_id}")
                ])
            if not has_active:
                response += "\n\n📭 Активних акаунтів не знайдено."
        elif isinstance(accounts, dict) and "error" in accounts:
            response += f"\n\n❌ Помилка завантаження акаунтів: {accounts.get('message', 'unknown')}"
        else:
            response += "\n\n📭 Акаунтів не знайдено."
    except Exception as e:
        logging.error(f"Error fetching user accounts: {e}")
        response += "\n\n❌ Помилка при отриманні списку акаунтів."
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=kb_buttons)
    await message.answer(response, parse_mode="HTML", reply_markup=keyboard)


@router.callback_query(F.data.startswith("rmacc_"))
@admin_only
async def cb_remove_account(callback: types.CallbackQuery):
    parts = callback.data.split("_")

    phone = parts[1]
    tg_id = parts[2]
    
    result = await backend_api.remove_account_from_user(phone, tg_id, callback.from_user.id)
    if "error" not in result:
        await callback.message.answer(f"✅ Доступ до акаунта <code>{phone}</code> для користувача <code>{tg_id}</code> видалено.", parse_mode="HTML")
        await callback.answer()
    else:
        await callback.answer(f"❌ Помилка: {result.get('message', 'Невідома помилка')}", show_alert=True)

@router.callback_query(F.data.startswith("ban_") | F.data.startswith("unban_"))
@admin_only
async def cb_toggle_user_ban(callback: types.CallbackQuery):
    user_id = callback.data.split("_")[1]
    result = await backend_api.toggle_user_ban(user_id, admin_id=callback.from_user.id)
    
    if "error" not in result:
        status_text = "заблокований" if result.get("isBanned") else "розблокований"
        await callback.message.answer(f"✅ Користувач <code>{user_id}</code>: <b>{status_text}</b>.", parse_mode="HTML")
        await callback.answer()
    else:
        await callback.answer(f"❌ Помилка: {result.get('message')}", show_alert=True)

@router.message(F.text == "📝 Вайтліст")
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

@router.message(F.text == "👥 Всі Користувачі")
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
        ban = "🚫" if user.get('isBanned') else "✅"
        wl = "📝" if user.get('isWhitelisted') else "❌"
        adm = "⭐" if user.get('isAdmin') else "👤"
        
        tg_id = user.get('telegramId') or user.get('id')
        username = html.escape(str(user.get('username', 'unknown')))
        
        text += (
            f"\n{adm} <b>@{username}</b>\n"
            f"   ID: <code>{tg_id}</code> | {ban} Ban | {wl} WL\n"
        )
    
    await message.answer(text, parse_mode="HTML")
