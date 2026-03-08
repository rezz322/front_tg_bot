from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

def get_admin_main_menu():
    buttons = [
        [KeyboardButton(text="👤 Інфо Користувача"), KeyboardButton(text="📊 Інфо Акаунта")],
        [KeyboardButton(text="🔑 Видати Ключ"), KeyboardButton(text="📚 Всі Акаунти")],
        [KeyboardButton(text="👥 Всі Користувачі"), KeyboardButton(text="📝 Вайтліст")],
        [KeyboardButton(text="📁 APK файли")]
    ]
    return ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)

def get_unauthorized_keyboard():
    buttons = [
        [KeyboardButton(text="❓ FAQ")]
    ]
    return ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)

def get_user_main_menu():
    buttons = [
        [KeyboardButton(text="📋 Мої Акаунти"), KeyboardButton(text="🔗 Прив'язати Акаунт")],
        [KeyboardButton(text="📥 APK файли")]
    ]
    return ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)

def get_apk_menu():
    buttons = [
        [KeyboardButton(text="📲 Клієнтський APK"), KeyboardButton(text="📲 Адмінський APK")],
        [KeyboardButton(text="⬅️ Назад")]
    ]
    return ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)

def get_refresh_key_inline(account_number: str):
    button = InlineKeyboardButton(text="🔄 Оновити Ключ", callback_data=f"refresh_{account_number}")
    return InlineKeyboardMarkup(inline_keyboard=[[button]])

def get_ban_user_inline(user_id):
    buttons = [[InlineKeyboardButton(text="🚫 Забанити", callback_data=f"ban_{user_id}")]]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_unban_user_inline(user_id):
    buttons = [[InlineKeyboardButton(text="✅ Розбанити", callback_data=f"unban_{user_id}")]]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_whitelist_user_inline(user_id):
    buttons = [[InlineKeyboardButton(text="📝 Додати до Вайтліста", callback_data=f"wladd_{user_id}")]]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_unwhitelist_user_inline(user_id):
    buttons = [[InlineKeyboardButton(text="❌ Видалити з Вайтліста", callback_data=f"wlrem_{user_id}")]]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_edit_acc_inline(acc_num: str):
    buttons = [
        [InlineKeyboardButton(text="📝 Редагувати ПІБ", callback_data=f"editacc_name_{acc_num}")],
        [InlineKeyboardButton(text="📱 Редагувати Номер", callback_data=f"editacc_phone_{acc_num}")],
        [InlineKeyboardButton(text="🔐 Редагувати PIN", callback_data=f"editacc_pin_{acc_num}")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_give_key_type_inline():
    # Only username remains as per user request
    buttons = [
        [InlineKeyboardButton(text="🆔 За Username", callback_data="gktype_user")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)
