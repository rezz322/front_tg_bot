import os
from aiogram import Router, types, F
from api_user import user_api as backend_api
from keyboards import get_user_main_menu, get_apk_menu
from config import FAQ_TEXT, CONTACT_LINK
from states import BindStates
from aiogram.fsm.context import FSMContext

router = Router()

@router.message(F.text == "📋 My Accounts")
async def show_accounts(message: types.Message):
    # For non-admins, show only their accounts
    accounts = await backend_api.get_user_accounts(message.from_user.id)
    print(accounts)
    if "error" in accounts:
        if accounts.get("status") == 404:
            await message.answer("📭 У вас немає прив'язаних акаунтів.")
        else:
            await message.answer("❌ Помилка при отриманні ваших акаунтів. Спробуйте пізніше.")
        return
    
    if not accounts:
        await message.answer("📭 У вас немає прив'язаних акаунтів.")
        return
    
    active_accounts = [acc for acc in accounts if not acc.get('isBanned')]
    
    if not active_accounts:
        await message.answer("📭 У вас немає прив'язаних акаунтів.")
        return

    text = "🔑 <b>Ваші акаунти:</b>\n"
    for acc in active_accounts:
        full_name = acc.get('full_name') or 'N/A'
        pin_code = acc.get('pin_code') or 'N/A'
        key = acc.get('key') or 'N/A'
        text += f"\n👤 {full_name}\n🔐 PIN: <code>{pin_code}</code>\n🆕 Ключ: <code>{key}</code>\n"
    
    await message.answer(text, parse_mode="HTML")

@router.message(F.text == "❓ FAQ")
async def show_faq(message: types.Message):
    text = f"{FAQ_TEXT}\n\nПо всім питанням: {CONTACT_LINK}"
    await message.answer(text)

@router.message(F.text == "📥 APKs")
async def show_apk_menu(message: types.Message):
    await message.answer("Оберіть APK для завантаження:", reply_markup=get_apk_menu())

@router.message(F.text == "🔗 Bind Account")
async def bind_account_start(message: types.Message, state: FSMContext):
    await message.answer("Введіть ваш номер телефону:")
    await state.set_state(BindStates.waiting_for_phone)

@router.message(BindStates.waiting_for_phone)
async def process_bind_phone(message: types.Message, state: FSMContext):
    await state.update_data(phone=message.text)
    await message.answer("Введіть ваш PIN-код:")
    await state.set_state(BindStates.waiting_for_pin)

@router.message(BindStates.waiting_for_pin)
async def process_bind_pin(message: types.Message, state: FSMContext):
    pin = message.text
    data = await state.get_data()
    await state.clear()
    
    result = await backend_api.auto_issue_key(
        user_id=message.from_user.id,
        phone=data.get("phone"),
        pin=pin
    )
    print(result)
    
    if "error" in result:
        msg = result.get('message', 'Перевірте дані')
        if "No matching available account" in msg or result.get("status") == 404:
            msg = "Акаунт з такими даними не знайдено або він вже привязаний."
        await message.answer(f"❌ Помилка привязки: {msg}")
    else:
        await message.answer(f"✅ Акаунт успішно привязано!\nВаш ключ: <code>{result.get('key')}</code>", parse_mode="HTML")

@router.message(F.text == "📲 Client APK")
async def download_client_apk(message: types.Message):
    channel_id = os.getenv("CHANNEL_ID")
    message_id = os.getenv("CLIENT_ID_APK")
    
    if not channel_id or not message_id:
        await message.answer("❌ Налаштування для завантаження Client APK відсутні.")
        return

    try:
        from config import CLIENT_APK_DESC
        await message.answer(CLIENT_APK_DESC)
        await message.bot.copy_message(
            chat_id=message.chat.id,
            from_chat_id=int(channel_id),
            message_id=int(message_id)
        )
    except Exception:
        pass

@router.message(F.text == "📲 Admin APK")
async def download_admin_apk(message: types.Message):
    channel_id = os.getenv("CHANNEL_ID")
    message_id = os.getenv("ADMIN_ID_APK")
    
    if not channel_id or not message_id:
        await message.answer("❌ Налаштування для завантаження Admin APK відсутні.")
        return

    try:
        from config import ADMIN_APK_DESC
        await message.answer(ADMIN_APK_DESC)
        await message.bot.copy_message(
            chat_id=message.chat.id,
            from_chat_id=int(channel_id),
            message_id=int(message_id)
        )
    except Exception:
        pass
