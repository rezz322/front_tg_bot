import html
from aiogram import Router, types, F
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
async def ask_user_id(message: types.Message, state: FSMContext):
    if not await check_is_admin(message.from_user.id): return
    await message.answer("Введіть ID користувача:")
    await state.set_state(AdminStates.waiting_for_user_id)

@router.message(AdminStates.waiting_for_user_id)
async def process_user_info(message: types.Message, state: FSMContext):
    if not await check_is_admin(message.from_user.id): return
    user_info = await backend_api.get_user_info(message.text, admin_id=message.from_user.id)
    await state.clear()
    
    if "error" in user_info:
        await message.answer(f"❌ Помилка: {user_info.get('message', 'Користувача не знайдено')}")
        return
    
    username = html.escape(str(user_info.get('username', 'N/A')))
    is_banned = user_info.get('isBanned', False)
    response = (
        f"👤 Користувач: <b>{username}</b>\n"
        f"🆔 DB ID: <code>{user_info.get('id')}</code>\n"
        f"📱 TG ID: <code>{user_info.get('telegramId')}</code>\n"
        f"🚫 Статус бану: {'Так' if is_banned else 'Ні'}"
    )
    
    tg_id = user_info.get('telegramId') or user_info.get('id')
    keyboard = keyboards.get_unban_user_inline(str(tg_id)) if is_banned else keyboards.get_ban_user_inline(str(tg_id))
    await message.answer(response, parse_mode="HTML", reply_markup=keyboard)

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
    
    acc_num = acc_info.get('phone') or 'N/A'
    acc_key = acc_info.get('key') or 'N/A'
    tg_user_id = acc_info.get('telegramUserId') or acc_info.get('userId')
    
    # Resolve username
    users = await backend_api.list_users(message.from_user.id)
    username = None
    if not isinstance(users, dict) or "error" not in users:
        for u in users:
            if str(u.get('id')) == str(tg_user_id) or str(u.get('telegramId')) == str(tg_user_id):
                username = u.get('username')
                break
    
    user_display = f"@{username}" if username else (f"<code>{tg_user_id}</code>" if tg_user_id else "❌ Немає")
    
    response = (
        f"📊 Акаунт №<code>{acc_num}</code>\n"
        f"🆕 Ключ: <code>{acc_key}</code>\n"
        f"👤 Користувач: {user_display}"
    )
    await message.answer(response, parse_mode="HTML", reply_markup=keyboards.get_refresh_key_inline(str(acc_num)))

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
async def ask_give_key_user(message: types.Message, state: FSMContext):
    if not await check_is_admin(message.from_user.id): return
    await message.answer("Введіть ID користувача, якому дати доступ:")
    await state.set_state(AdminStates.waiting_for_give_key_user)

@router.message(AdminStates.waiting_for_give_key_user)
async def process_give_key_user(message: types.Message, state: FSMContext):
    if not await check_is_admin(message.from_user.id): return
    await state.update_data(target_user_id=message.text)
    await message.answer("Введіть номер акаунта:")
    await state.set_state(AdminStates.waiting_for_give_key_number)

@router.message(AdminStates.waiting_for_give_key_number)
async def process_give_key_number(message: types.Message, state: FSMContext):
    if not await check_is_admin(message.from_user.id): return
    data = await state.get_data()
    target_user_id = data.get("target_user_id")
    acc_number = message.text
    
    result = await backend_api.give_key(target_user_id, acc_number, admin_id=message.from_user.id)
    await state.clear()
    
    if "error" in result:
        await message.answer(f"❌ Помилка: {result.get('message', 'Не вдалося видати ключ')}")
    else:
        await message.answer(f"✅ Користувачу <code>{target_user_id}</code> надано доступ до акаунта <code>{acc_number}</code>.", parse_mode="HTML")

@router.message(F.text == "📚 All Accounts")
async def list_all_accounts(message: types.Message):
    if not await check_is_admin(message.from_user.id): return
    
    # Fetch accounts and users to create a mapping
    accounts = await backend_api.list_accounts(message.from_user.id)
    users = await backend_api.list_users(message.from_user.id)
    
    if "error" in accounts or "error" in users:
        await message.answer("❌ Помилка при отриманні даних з сервера.")
        return
    
    # Create mapping: ID -> Username
    user_map = {}
    for u in users:
        u_name = u.get('username') or 'unknown'
        if u.get('id'): user_map[str(u.get('id'))] = u_name
        if u.get('telegramId'): user_map[str(u.get('telegramId'))] = u_name

    if not accounts:
        await message.answer("📭 Акаунти відсутні в системі.")
        return
    
    text = "📚 <b>Всі акаунти в системі:</b>\n"
    for acc in accounts:
        # Get numerical IDs
        tg_user_id = acc.get('telegramUserId') or acc.get('userId')
        
        # Resolve username from our map
        username = user_map.get(str(tg_user_id)) if tg_user_id else None
        
        # Display: @username or ID or placeholder
        user_display = f"@{username}" if username else (f"<code>{tg_user_id}</code>" if tg_user_id else '❌ Немає')
        
        acc_num = acc.get('phone') or 'N/A'
        acc_key = acc.get('key') or 'N/A'
        
        text += (
            f"\n🔹 №<code>{acc_num}</code>\n"
            f"   🆕 Ключ: <code>{acc_key}</code>\n"
            f"   👤 Користувач: {user_display}\n"
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
        admin_status = "⭐ Адмін" if user.get('isAdmin') else "👤 Користувач"
        # Using telegramId instead of id based on user request
        tg_id = user.get('telegramId') or user.get('id')
        username = html.escape(str(user.get('username', 'unknown')))
        text += f"\n{admin_status} | <b>{username}</b>\n   TG ID: <code>{tg_id}</code>\n   Статус: {ban_status}\n"
    
    await message.answer(text, parse_mode="HTML")
