from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def get_confirm_keyboard(yes_callback: str, no_callback: str) -> InlineKeyboardMarkup:
    """Returns a generic confirmation keyboard."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Так", callback_data=yes_callback),
            InlineKeyboardButton(text="❌ Ні", callback_data=no_callback)
        ]
    ])

def get_back_inline(callback_data: str) -> InlineKeyboardMarkup:
    """Returns a keyboard with a single back button."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⬅️ Назад", callback_data=callback_data)]
    ])
