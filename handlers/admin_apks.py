from aiogram import Router, types, F
import keyboards
from handlers.admin_common import admin_only

router = Router()

@router.message(F.text == "📁 APK файли")
@admin_only
async def show_admin_apk_menu(message: types.Message):
    await message.answer("Оберіть APK для завантаження:", reply_markup=keyboards.get_apk_menu())
