import os
from aiogram import Router, types, F
from api_client import backend_api
from keyboards import get_user_main_menu, get_apk_menu

router = Router()

@router.message(F.text == "📋 Available Accounts")
async def show_accounts(message: types.Message):
    accounts = await backend_api.get_available_accounts()
    if "error" in accounts:
        await message.answer("❌ Помилка при отриманні списку акаунтів.")
        return
    
    if not accounts:
        await message.answer("📭 Немає доступних акаунтів.")
        return
    
    text = "🔑 Доступні ключі:\n" + "\n".join([f"• <code>{acc.get('key')}</code>" for acc in accounts])
    await message.answer(text, parse_mode="HTML")

@router.message(F.text == "📁 APKs")
@router.message(F.text == "📥 Download Client APK")
@router.message(F.text == "📥 Download Admin APK")
async def show_apk_menu(message: types.Message):
    await message.answer("Оберіть APK для завантаження:", reply_markup=get_apk_menu())

@router.message(F.text == "📲 Client APK")
async def download_client_apk(message: types.Message):
    # Hardcoded forwarding: Client ID 6 from specific channel
    channel_id = int(os.getenv("CHANNEL_ID"))
    try:
        await message.bot.copy_message(
            chat_id=message.chat.id,
            from_chat_id=channel_id,
            message_id=int(os.getenv("CLIENT_ID_APK"))
        )
    except Exception as e:
        await message.answer(f"❌ Помилка завантаження Client APK: {e}")

@router.message(F.text == "📲 Admin APK")
async def download_admin_apk(message: types.Message):
    # Hardcoded forwarding: Admin ID 7 from specific channel
    channel_id = int(os.getenv("CHANNEL_ID"))
    try:
        await message.bot.copy_message(
            chat_id=message.chat.id,
            from_chat_id=channel_id,
            message_id=int(os.getenv("ADMIN_ID_APK"))
        )
    except Exception as e:
        await message.answer(f"❌ Помилка завантаження Admin APK: {e}")
