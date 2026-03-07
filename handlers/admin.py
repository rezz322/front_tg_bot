import html
from aiogram import Router, types, F
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from api_client import backend_api
import keyboards
from states import AdminStates

router = Router()

# Helper check for admin
async def check_is_admin(user_id: int):
    admin_response = await backend_api.check_admin(user_id)
    return admin_response.get("isAdmin", False) if isinstance(admin_response, dict) else False

@router.message(F.text == "👤 Info User")
async def ask_user_username(message: types.Message, state: FSMContext):
    if not await check_is_admin(message.from_user.id): return
    await message.answer("Введіть Username користувача (без @):")
    await state.set_state(AdminStates.waiting_for_user_id)

@router.message(AdminStates.waiting_for_user_id)
async def process_user_info(message: types.Message, state: FSMContext):
    if not await check_is_admin(message.from_user.id): return
    # Now searching by username
    user_info = await backend_api.get_user_info_by_username(message.text.replace("@", ""), admin_id=message.from_user.id)
    await state.clear()
    
    if "error" in user_info:
        await message.answer(f"❌ Помилка: {user_info.get('message', 'Користувача не знайдено')}")
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
    
    # Create inline keyboard with multiple rows
    kb_buttons = []
    
    # Ban/Unban row
    kb_buttons.append([
        InlineKeyboardButton(text="✅ Unban" if is_banned else "🚫 Ban", 
                             callback_data=f"{'unban' if is_banned else 'ban'}_{tg_id}")
    ])
    
    # Whitelist row
    kb_buttons.append([
        InlineKeyboardButton(text="❌ Rem WL" if is_whitelisted else "📝 Add WL", 
                             callback_data=f"{'wlrem' if is_whitelisted else 'wladd'}_{tg_id}")
    ])
    
    # Accounts removal rows (2 accounts per row)
    accounts = user_info.get('accounts', [])
    if accounts:
        temp_row = []
        for i, acc in enumerate(accounts):
            acc_id = acc.get('id')
            phone = acc.get('phone', 'N/A')
            temp_row.append(InlineKeyboardButton(text=f"🗑 {phone}", callback_data=f"takeaway_{acc_id}_{tg_id}"))
            
            if len(temp_row) == 2:
                kb_buttons.append(temp_row)
                temp_row = []
        if temp_row:
            kb_buttons.append(temp_row)
            
    keyboard = InlineKeyboardMarkup(inline_keyboard=kb_buttons)
    await message.answer(response, parse_mode="HTML", reply_markup=keyboard)

@router.callback_query(F.data.startswith("takeaway_"))
async def cb_takeaway_account(callback: types.CallbackQuery):
    if not await check_is_admin(callback.from_user.id): return
    
    parts = callback.data.split("_")
    acc_id = parts[1]
    tg_id = parts[2]
    
    result = await backend_api.take_away_account(int(acc_id), admin_id=callback.from_user.id)
    
    if "error" in result:
        await callback.answer(f"❌ Помилка: {result.get('message')}", show_alert=True)
    else:
        await callback.answer("✅ Акаунт відв'язано!")
        # Refresh user info
        user_info = await backend_api.get_user_info(tg_id, admin_id=callback.from_user.id)
        if "error" not in user_info:
            # Rebuild keyboard (reuse logic or notify and edit message)
            await callback.message.edit_text("🔄 Оновлення даних...")
            # We can't easily call process_user_info from here, but we can manually recreate logic
            # or just send a new message. Let's send a text update.
            await callback.message.answer(f"✅ Акаунт {acc_id} успішно відв'язано від користувача {tg_id}.")
            await callback.message.delete()

@router.message(F.text == "📊 Info Account")
async def ask_account_number(message: types.Message, state: FSMContext):
    if not await check_is_admin(message.from_user.id): return
    await message.answer("Введіть номер акаунта:")
    await state.set_state(AdminStates.waiting_for_account_number)

@router.message(AdminStates.waiting_for_account_number)
async def process_account_info(message: types.Message, state: FSMContext):
    if not await check_is_admin(message.from_user.id): return
    acc_info = await backend_api.get_account_info(message.text, admin_id=message.from_user.id)
    await state.clear()
    
    if "error" in acc_info:
        await message.answer("❌ Акаунт не знайдено.")
        return
    
    acc_id = acc_info.get('id')
    acc_num = acc_info.get('phone') or 'N/A'
    acc_key = acc_info.get('key') or 'N/A'
    is_acc_banned = acc_info.get('isBanned', False)
    
    tg_users = acc_info.get('telegramUsers', [])
    if tg_users:
        user_displays = []
        for tu in tg_users:
            uname = tu.get('username')
            tid = tu.get('telegramId')
            user_displays.append(f"@{uname}" if uname else f"<code>{tid}</code>")
        user_display = ", ".join(user_displays)
    else:
        user_display = "❌ Немає"
    
    full_name = acc_info.get('full_name') or 'N/A'
    pin_code = acc_info.get('pin_code') or 'N/A'
    expires_at = acc_info.get('expiresAt')
    expires_str = expires_at.split('T')[0] if expires_at else '♾️'
    
    acc_ban_status = "🚫 ЗАБАНЕНИЙ" if is_acc_banned else "✅ Активний"
    
    response = (
        f"📊 Акаунт: <code>{acc_num}</code>\n"
        f"👤 ПІБ: <b>{html.escape(full_name)}</b>\n"
        f"🔐 PIN: <code>{pin_code}</code>\n"
        f"⏳ Срок: <code>{expires_str}</code>\n"
        f"🆕 Ключ: <code>{acc_key}</code>\n"
        f"🛡️ Статус: {acc_ban_status}\n"
        f"👥 Користувачі: {user_display}"
    )
    
    # Inline keyboard
    kb_buttons = [
        [InlineKeyboardButton(text="🔄 Refresh Key", callback_data=f"refresh_{acc_num}")],
        [InlineKeyboardButton(text="📝 Edit Details", callback_data=f"edit_acc_{acc_num}")],
        [InlineKeyboardButton(text="✅ Unban Acc" if is_acc_banned else "🚫 Ban Acc", callback_data=f"accban_{acc_id}_{acc_num}")]
    ]
    reply_markup = InlineKeyboardMarkup(inline_keyboard=kb_buttons)
    await message.answer(response, parse_mode="HTML", reply_markup=reply_markup)

@router.callback_query(F.data.startswith("accban_"))
async def cb_toggle_account_ban(callback: types.CallbackQuery):
    if not await check_is_admin(callback.from_user.id): return
    
    parts = callback.data.split("_")
    acc_id = parts[1]
    acc_num = parts[2]
    
    result = await backend_api.toggle_account_ban(int(acc_id), admin_id=callback.from_user.id)
    
    if "error" in result:
        await callback.answer(f"❌ Помилка: {result.get('message')}", show_alert=True)
    else:
        status = "забанений" if result.get("isBanned") else "розбанений"
        await callback.answer(f"✅ Акаунт {acc_num} {status}!")
        # Update original message
        # We can simulate process_account_info result or just notify
        await callback.message.answer(f"✅ Статус акаунта <code>{acc_num}</code> змінено на: {status}.", parse_mode="HTML")
        await callback.message.delete()

@router.callback_query(F.data.startswith("refresh_"))
async def cb_refresh_key(callback: types.CallbackQuery):
    if not await check_is_admin(callback.from_user.id):
        await callback.answer("🚫 У вас немає прав адміністратора.", show_alert=True)
        return
    acc_num = callback.data.split("_")[1]
    result = await backend_api.refresh_account_key(acc_num, admin_id=callback.from_user.id)
    
    if "error" in result:
        await callback.answer("❌ Помилка оновлення.")
    else:
        await callback.message.answer(f"✅ Ключ для акаунта <code>{acc_num}</code> оновлено!\nНовий ключ: <code>{result.get('key')}</code>", parse_mode="HTML")
        await callback.answer()

@router.callback_query(F.data.startswith("ban_"))
async def cb_ban_user(callback: types.CallbackQuery):
    if not await check_is_admin(callback.from_user.id):
        await callback.answer("🚫 У вас немає прав адміністратора.", show_alert=True)
        return
    user_id = callback.data.split("_")[1]
    result = await backend_api.ban_user(user_id, admin_id=callback.from_user.id)
    
    if "error" in result:
        await callback.answer("❌ Помилка при бані.")
    else:
        await callback.message.answer(f"🚫 Користувач <code>{user_id}</code> заблокований. Ключі оновлено.", parse_mode="HTML")
        await callback.answer()

@router.callback_query(F.data.startswith("unban_"))
async def cb_unban_user(callback: types.CallbackQuery):
    if not await check_is_admin(callback.from_user.id):
        await callback.answer("🚫 У вас немає прав адміністратора.", show_alert=True)
        return
    user_id = callback.data.split("_")[1]
    result = await backend_api.unban_user(user_id, admin_id=callback.from_user.id)
    
    if "error" in result:
        await callback.answer("❌ Помилка при розбані.")
    else:
        await callback.message.answer(f"✅ Користувач <code>{user_id}</code> розблокований.", parse_mode="HTML")
        await callback.answer()

@router.message(F.text == "🔑 Give Key")
async def start_give_key_flow(message: types.Message, state: FSMContext):
    if not await check_is_admin(message.from_user.id): return
    await message.answer("Введіть Username користувача (без @):")
    await state.set_state(AdminStates.waiting_for_give_key_username)

@router.message(AdminStates.waiting_for_give_key_username)
async def process_gk_username(message: types.Message, state: FSMContext):
    if not await check_is_admin(message.from_user.id): return
    await state.update_data(target_username=message.text.replace("@", ""))
    await message.answer("Введіть номер акаунта:")
    await state.set_state(AdminStates.waiting_for_give_key_number)

@router.message(AdminStates.waiting_for_give_key_number)
async def process_give_key_number(message: types.Message, state: FSMContext):
    if not await check_is_admin(message.from_user.id): return
    await state.update_data(acc_number=message.text)
    await message.answer("Введіть кількість днів (0 для безстрокового):")
    await state.set_state(AdminStates.waiting_for_give_key_days)

@router.message(AdminStates.waiting_for_give_key_days)
async def process_give_key_days(message: types.Message, state: FSMContext):
    if not await check_is_admin(message.from_user.id): return
    try:
        days = int(message.text)
    except ValueError:
        await message.answer("Будь ласка, введіть число.")
        return
        
    data = await state.get_data()
    await state.clear()
    
    gk_type = data.get("gk_type") or "user" # Default to user
    acc_number = data.get("acc_number")
    days_val = days if days > 0 else None
    
    if gk_type == "id":
        # Keep as fallback but we removed the UI for it
        result = await backend_api.give_key(data.get("target_user_id"), acc_number, admin_id=message.from_user.id, days=days_val)
    else:
        result = await backend_api.give_key_by_username(data.get("target_username"), acc_number, admin_id=message.from_user.id, days=days_val)
    
    if "error" in result:
        await message.answer(f"❌ Помилка: {result.get('message', 'Не вдалося видати ключ')}")
    else:
        status_msg = f"на {days} днів" if days > 0 else "безстроково"
        await message.answer(f"✅ Доступ надано {status_msg}.\nАкаунт: <code>{acc_number}</code>", parse_mode="HTML")

@router.message(F.text == "📝 Whitelist")
async def ask_whitelist_username(message: types.Message, state: FSMContext):
    if not await check_is_admin(message.from_user.id): return
    await message.answer("Введіть Username користувача (без @) для перемикання вайтліста:")
    await state.set_state(AdminStates.waiting_for_whitelist_username)

@router.message(AdminStates.waiting_for_whitelist_username)
async def process_whitelist_username(message: types.Message, state: FSMContext):
    if not await check_is_admin(message.from_user.id): return
    username = message.text.replace("@", "")
    result = await backend_api.toggle_whitelist_by_username(username, admin_id=message.from_user.id)
    await state.clear()
    
    if "error" in result:
        await message.answer(f"❌ Помилка: {result.get('message', 'Користувача не знайдено')}")
    else:
        status = "доданий до" if result.get("isWhitelisted") else "видалений з"
        await message.answer(f"✅ Користувач @{username} {status} вайтліста.")

@router.callback_query(F.data.startswith("wladd_") | F.data.startswith("wlrem_"))
async def cb_toggle_whitelist(callback: types.CallbackQuery):
    if not await check_is_admin(callback.from_user.id):
        await callback.answer("🚫 У вас немає прав адміністратора.", show_alert=True)
        return
    
    parts = callback.data.split("_")
    action = parts[0]
    user_id = parts[1]
    result = await backend_api.toggle_whitelist(user_id, admin_id=callback.from_user.id)
    
    if "error" in result:
        await callback.answer("❌ Помилка перемикання вайтліста.")
    else:
        status = "доданий до" if result.get("isWhitelisted") else "видалений з"
        await callback.message.answer(f"✅ Користувач <code>{user_id}</code> {status} вайтліста.", parse_mode="HTML")
        await callback.answer()

@router.message(F.text == "📚 All Accounts")
async def list_all_accounts(message: types.Message):
    if not await check_is_admin(message.from_user.id): return
    
    # Fetch accounts
    accounts = await backend_api.list_accounts(message.from_user.id)
    
    if "error" in accounts:
        await message.answer("❌ Помилка при отриманні даних з сервера.")
        return

    if not accounts:
        await message.answer("📭 Акаунти відсутні в системі.")
        return
    
    text = "📚 <b>Всі акаунти в системі:</b>\n"
    if not accounts:
        await message.answer("📭 Акаунти відсутні в системі.")
        return

    for acc in accounts:
        tg_users = acc.get('telegramUsers', [])
        is_acc_banned = acc.get('isBanned', False)
        
        if tg_users:
            user_displays = []
            for tu in tg_users:
                uname = tu.get('username')
                tid = tu.get('telegramId')
                user_displays.append(f"@{uname}" if uname else f"<code>{tid}</code>")
            user_display = ", ".join(user_displays)
        else:
            user_display = "❌ Немає"
        
        ban_prefix = "🚫 " if is_acc_banned else ""
        
        acc_num = acc.get('phone') or 'N/A'
        acc_key = acc.get('key') or 'N/A'
        
        full_name = acc.get('full_name') or 'N/A'
        pin_code = acc.get('pin_code') or 'N/A'
        
        text += (
            f"\n🔹 {ban_prefix}<code>{acc_num}</code> | {html.escape(full_name)}\n"
            f"   🔐 PIN: <code>{pin_code}</code>\n"
            f"   🆕 Ключ: <code>{acc_key}</code>\n"
            f"   👤 Користувачі: {user_display}\n"
        )
    
    await message.answer(text, parse_mode="HTML")

@router.message(F.text == "👥 All Users")
async def list_all_users(message: types.Message):
    if not await check_is_admin(message.from_user.id): return
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
@router.callback_query(F.data.startswith("edit_acc_"))
async def cb_edit_acc_start(callback: types.CallbackQuery, state: FSMContext):
    if not await check_is_admin(callback.from_user.id): return
    acc_num = callback.data.split("_")[2]
    await callback.message.answer(f"Що саме редагуємо для акаунта {acc_num}?", reply_markup=keyboards.get_edit_acc_inline(acc_num))
    await callback.answer()

@router.callback_query(F.data.startswith("editacc_"))
async def cb_edit_acc_field(callback: types.CallbackQuery, state: FSMContext):
    if not await check_is_admin(callback.from_user.id): return
    _, field, acc_num = callback.data.split("_")
    
    field_names = {"name": "ПІБ", "phone": "Номер", "pin": "PIN"}
    await state.update_data(edit_acc_num=acc_num, edit_field=field)
    
    await callback.message.answer(f"Введіть нове значення для поля {field_names.get(field)}:")
    await state.set_state(AdminStates.waiting_for_edit_acc_value)
    await callback.answer()

@router.message(AdminStates.waiting_for_edit_acc_value)
async def process_edit_acc_value(message: types.Message, state: FSMContext):
    if not await check_is_admin(message.from_user.id): return
    data = await state.get_data()
    await state.clear()
    
    field_map = {"name": "full_name", "phone": "phone", "pin": "pin_code"}
    db_field = field_map.get(data.get("edit_field"))
    acc_num = data.get("edit_acc_num")
    
    # Needs account ID for update_account. Let's fetch info first or rely on phone if API supports targeting by phone.
    # Current backend Patch /accounts/:id uses ID.
    acc_info = await backend_api.get_account_info(acc_num, admin_id=message.from_user.id)
    if "error" in acc_info:
        await message.answer("❌ Помилка при отриманні ID акаунта.")
        return
        
    acc_id = acc_info.get("id")
    result = await backend_api.update_account(acc_id, {db_field: message.text}, admin_id=message.from_user.id)
    
    if "error" in result:
        await message.answer(f"❌ Помилка оновлення: {result.get('message')}")
    else:
        await message.answer(f"✅ Поле оновлено!")

@router.message(F.text == "📁 APKs")
async def show_admin_apk_menu(message: types.Message):
    if not await check_is_admin(message.from_user.id): return
    await message.answer("Оберіть APK для завантаження:", reply_markup=keyboards.get_apk_menu())
