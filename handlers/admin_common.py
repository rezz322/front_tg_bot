import functools
import inspect
from api_user import user_api as backend_api

async def check_is_admin(user_id: int):
    """Checks if a user has admin privileges."""
    access = await backend_api.check_admin(user_id)
    return access.get("isAdmin", False) if isinstance(access, dict) else False

def admin_only(handler):
    """Decorator to restrict handler access to admins only."""
    @functools.wraps(handler)
    async def wrapper(event, **kwargs):
        user_id = event.from_user.id
        if not await check_is_admin(user_id):
            return
        
        # Get the handler's signature to filter kwargs
        sig = inspect.signature(handler)
        filtered_kwargs = {k: v for k, v in kwargs.items() if k in sig.parameters}
        
        # Determine the name of the first parameter (usually message or callback_query)
        params = list(sig.parameters.items())
        if not params:
            return await handler()
            
        first_param_name = params[0][0]
        
        # If the first parameter is already in filtered_kwargs, just call it
        if first_param_name in filtered_kwargs:
            return await handler(**filtered_kwargs)
        
        # Otherwise, pass the event as the first positional argument
        return await handler(event, **filtered_kwargs)
    return wrapper
