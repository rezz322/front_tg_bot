from typing import Any, Awaitable, Callable, Dict
from aiogram import BaseMiddleware
from aiogram.types import Message
from api_user import user_api as backend_api

class BanMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: Dict[str, Any]
    ) -> Any:
        user_id = event.from_user.id
        
        # Check user status
        user_info = await backend_api.get_user_by_id(user_id)
        
        if isinstance(user_info, dict) and user_info.get("isBanned"):
            await event.answer("🚫 Ви заблоковані адміністратором і не можете користуватися ботом.")
            return

        return await handler(event, data)
