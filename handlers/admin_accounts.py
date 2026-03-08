import html
from aiogram import Router, types, F
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from api_admin import admin_api as backend_api
import keyboards
from states import AdminStates
from handlers.admin_common import admin_only
from utils.formatters import format_account_info

router = Router()

@router.message(F.text == "📊 Інфо Акаунта")
@admin_only
async def ask_account_number(message: types.Message, state: FSMContext):
    await message.answer("Введіть номер акаунта:")
    await state.set_state(AdminStates.waiting_for_account_number)

@router.message(AdminStates.waiting_for_account_number)
@admin_only
async def process_account_info(message: types.Message, state: FSMContext):
    acc_info = await backend_api.get_account_info(message.text, admin_id=message.from_user.id)
    await state.clear()
    
    if "error" in acc_info:
        await message.answer("❌ Акаунт не знайдено.")
        return
    
    response = format_account_info(acc_info)
    acc_id = acc_info.get('id')
    acc_num = acc_info.get('phone') or 'N/A'
    is_acc_banned = acc_info.get('isBanned', False)
    
    kb_buttons = [
        [InlineKeyboardButton(text="🔄 Оновити Ключ", callback_data=f"refresh_{acc_num}")],
        [InlineKeyboardButton(text="📝 Редагувати Дані", callback_data=f"edit_acc_{acc_num}")],
        [InlineKeyboardButton(text="✅ Розбанити Акк" if is_acc_banned else "🚫 Забанити Акк", callback_data=f"accban_{acc_id}_{acc_num}")]
    ]
    await message.answer(response, parse_mode="HTML", reply_markup=InlineKeyboardMarkup(inline_keyboard=kb_buttons))

@router.callback_query(F.data.startswith("accban_"))
@admin_only
async def cb_toggle_account_ban(callback: types.CallbackQuery):
    _, acc_id, acc_num = callback.data.split("_")
    result = await backend_api.toggle_account_ban(int(acc_id), admin_id=callback.from_user.id)
    if "error" not in result:
        status = "забанений" if result.get("isBanned") else "розбанений"
        await callback.answer(f"✅ Акаунт {acc_num} {status}!")
        await callback.message.answer(f"✅ Статус акаунта <code>{acc_num}</code> змінено на: {status}.", parse_mode="HTML")
        await callback.message.delete()

@router.callback_query(F.data.startswith("refresh_"))
@admin_only
async def cb_refresh_key(callback: types.CallbackQuery):
    acc_num = callback.data.split("_")[1]
    result = await backend_api.refresh_account_key(acc_num, admin_id=callback.from_user.id)
    if "error" not in result:
        await callback.message.answer(f"✅ Ключ для акаунта <code>{acc_num}</code> оновлено!\nНовий ключ: <code>{result.get('key')}</code>", parse_mode="HTML")
        await callback.answer()

@router.message(F.text == "🔑 Видати Ключ")
@admin_only
async def start_give_key_flow(message: types.Message, state: FSMContext):
    await message.answer("Введіть Username користувача (без @):")
    await state.set_state(AdminStates.waiting_for_give_key_username)

@router.message(AdminStates.waiting_for_give_key_username)
@admin_only
async def process_gk_username(message: types.Message, state: FSMContext):
    await state.update_data(target_username=message.text.replace("@", ""))
    await message.answer("Введіть номер акаунта:")
    await state.set_state(AdminStates.waiting_for_give_key_number)

@router.message(AdminStates.waiting_for_give_key_number)
@admin_only
async def process_give_key_number(message: types.Message, state: FSMContext):
    await state.update_data(acc_number=message.text)
    await message.answer("Введіть кількість днів (0 для безстрокового):")
    await state.set_state(AdminStates.waiting_for_give_key_days)

@router.message(AdminStates.waiting_for_give_key_days)
@admin_only
async def process_give_key_days(message: types.Message, state: FSMContext):
    try:
        days = int(message.text)
    except ValueError:
        await message.answer("Будь ласка, введіть число.")
        return
        
    data = await state.get_data()
    await state.clear()
    
    acc_number = data.get("acc_number")
    days_val = days if days > 0 else None
    result = await backend_api.give_key_by_username(data.get("target_username"), acc_number, admin_id=message.from_user.id, days=days_val)
    
    if "error" in result:
        print(result)
        await message.answer("❌ Помилка. Перевірте дані.")
    else:
        status_msg = f"на {days} днів" if days > 0 else "безстроково"
        await message.answer(f"✅ Доступ надано {status_msg}.\nАкаунт: <code>{acc_number}</code>", parse_mode="HTML")

@router.message(F.text == "📚 Всі Акаунти")
@admin_only
async def list_all_accounts(message: types.Message):
    accounts = await backend_api.list_accounts(message.from_user.id)
    if "error" in accounts or not accounts:
        await message.answer("❌ Помилка або акаунти відсутні.")
        return

    text = "📚 <b>Всі акаунти в системі:</b>\n"
    for acc in accounts:
        user = acc.get('user')
        user_display = f"@{user.get('username')}" if user and user.get('username') else str(user.get('telegramId')) if user else "❌"
        status = "🚫 " if acc.get('isBanned') else "🔹 "
        
        text += (
            f"\n{status}<code>{acc.get('phone')}</code> | {html.escape(acc.get('full_name') or 'N/A')}\n"
            f"   PIN: <code>{acc.get('pin_code')}</code> | Key: <code>{acc.get('key')}</code>\n"
            f"   👥 {user_display}\n"
        )
    await message.answer(text, parse_mode="HTML")

@router.callback_query(F.data.startswith("edit_acc_"))
@admin_only
async def cb_edit_acc_start(callback: types.CallbackQuery, state: FSMContext):
    acc_num = callback.data.split("_")[2]
    await callback.message.answer(f"Що саме редагуємо для акаунта {acc_num}?", reply_markup=keyboards.get_edit_acc_inline(acc_num))
    await callback.answer()

@router.callback_query(F.data.startswith("editacc_"))
@admin_only
async def cb_edit_acc_field(callback: types.CallbackQuery, state: FSMContext):
    _, field, acc_num = callback.data.split("_")
    field_names = {"name": "ПІБ", "phone": "Номер", "pin": "PIN"}
    await state.update_data(edit_acc_num=acc_num, edit_field=field)
    await callback.message.answer(f"Введіть нове значення для поля {field_names.get(field)}:")
    await state.set_state(AdminStates.waiting_for_edit_acc_value)
    await callback.answer()

@router.message(AdminStates.waiting_for_edit_acc_value)
@admin_only
async def process_edit_acc_value(message: types.Message, state: FSMContext):
    data = await state.get_data()
    await state.clear()
    
    field_map = {"name": "full_name", "phone": "phone", "pin": "pin_code"}
    db_field = field_map.get(data.get("edit_field"))
    acc_num = data.get("edit_acc_num")
    
    acc_info = await backend_api.get_account_info(acc_num, admin_id=message.from_user.id)
    if "error" not in acc_info:
        await backend_api.update_account(acc_info.get("id"), {db_field: message.text}, admin_id=message.from_user.id)
        await message.answer(f"✅ Поле оновлено!")
