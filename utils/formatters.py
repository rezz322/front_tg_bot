import html

def format_user_info(user_data: dict) -> str:
    """Formats user information into a consistent HTML string."""
    tg_id = user_data.get('telegramId', 'N/A')
    username = user_data.get('username', 'unknown')
    is_whitelisted = "✅ Так" if user_data.get('isWhitelisted') else "❌ Ні"
    is_banned = "🚫 Так" if user_data.get('isBanned') else "✅ Ні"
    limit = user_data.get('accountLimit', -1)
    limit_str = "♾️ Необмежено" if limit == -1 else f"<code>{limit}</code>"
    
    res = (
        f"👤 <b>Користувач:</b> @{username}\n"
        f"🆔 <b>TG ID:</b> <code>{tg_id}</code>\n"
        f"⚪️ <b>Вайтліст:</b> {is_whitelisted}\n"
        f"🔒 <b>Бан:</b> {is_banned}\n"
        f"📊 <b>Ліміт акаунтів:</b> {limit_str}"
    )
    return res

def format_account_info(acc_data: dict) -> str:
    """Formats account information into a consistent HTML string."""
    if not acc_data:
        return "❌ Дані акаунта відсутні"
        
    phone = acc_data.get('phone', 'N/A')
    key = acc_data.get('key', 'Немає')
    is_banned = "🚫 Забанений" if acc_data.get('isBanned') else "✅ Активний"
    full_name = html.escape(str(acc_data.get('full_name', 'Не вказано')))
    pin = acc_data.get('pin_code', '****')
    
    expires_at = acc_data.get('expiresAt')
    try:
        expires_str = expires_at.split('T')[0] if expires_at and isinstance(expires_at, str) else '♾️'
    except Exception:
        expires_str = '♾️'
    
    user = acc_data.get('user')
    if isinstance(user, dict):
        username = user.get('username')
        tg_id = user.get('telegramId')
        user_display = f"@{username}" if username else f"<code>{tg_id}</code>" if tg_id else "❓ Невідомо"
    else:
        user_display = "❌ Немає"
    
    res = (
        f"📊 <b>Акаунт:</b> <code>{phone}</code>\n"
        f"👤 <b>ПІБ:</b> {full_name}\n"
        f"🔐 <b>PIN:</b> <code>{pin}</code>\n"
        f"⏳ <b>Срок:</b> <code>{expires_str}</code>\n"
        f"🔑 <b>Ключ:</b> <code>{key}</code>\n"
        f"🛡️ <b>Статус:</b> {is_banned}\n"
        f"👥 <b>Користувачі:</b> {user_display}"
    )
    return res
