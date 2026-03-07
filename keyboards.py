from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

def get_admin_main_menu():
    buttons = [
        [KeyboardButton(text="👤 Info User"), KeyboardButton(text="📊 Info Account")],
        [KeyboardButton(text="🔑 Give Key"), KeyboardButton(text="📚 All Accounts")],
        [KeyboardButton(text="👥 All Users"), KeyboardButton(text="📝 Whitelist")],
        [KeyboardButton(text="📁 APKs")]
    ]
    return ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)

def get_unauthorized_keyboard():
    buttons = [
        [KeyboardButton(text="❓ FAQ")]
    ]
    return ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)

def get_user_main_menu():
    buttons = [
        [KeyboardButton(text="📋 My Accounts"), KeyboardButton(text="🔗 Bind Account")],
        [KeyboardButton(text="📥 APKs")]
    ]
    return ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)

def get_apk_menu():
    buttons = [
        [KeyboardButton(text="📲 Client APK"), KeyboardButton(text="📲 Admin APK")],
        [KeyboardButton(text="⬅️ Back")]
    ]
    return ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)

def get_refresh_key_inline(account_number: str):
    button = InlineKeyboardButton(text="🔄 Refresh Key", callback_data=f"refresh_{account_number}")
    return InlineKeyboardMarkup(inline_keyboard=[[button]])

def get_ban_user_inline(user_id):
    buttons = [[InlineKeyboardButton(text="🚫 Ban User", callback_data=f"ban_{user_id}")]]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_unban_user_inline(user_id):
    buttons = [[InlineKeyboardButton(text="✅ Unban User", callback_data=f"unban_{user_id}")]]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_whitelist_user_inline(user_id):
    buttons = [[InlineKeyboardButton(text="📝 Add to Whitelist", callback_data=f"wladd_{user_id}")]]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_unwhitelist_user_inline(user_id):
    buttons = [[InlineKeyboardButton(text="❌ Remove from Whitelist", callback_data=f"wlrem_{user_id}")]]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_edit_acc_inline(acc_num: str):
    buttons = [
        [InlineKeyboardButton(text="📝 Edit Full Name", callback_data=f"editacc_name_{acc_num}")],
        [InlineKeyboardButton(text="📱 Edit Phone", callback_data=f"editacc_phone_{acc_num}")],
        [InlineKeyboardButton(text="🔐 Edit PIN", callback_data=f"editacc_pin_{acc_num}")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_give_key_type_inline():
    # Only username remains as per user request
    buttons = [
        [InlineKeyboardButton(text="🆔 By Username", callback_data="gktype_user")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)
