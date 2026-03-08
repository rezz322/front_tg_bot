import aiohttp
from config import API_BASE_URL

class BaseAPI:
    def __init__(self, base_url: str = API_BASE_URL):
        self.base_url = base_url

    async def _handle_error(self, response):
        try:
            error_data = await response.json()
            raw_msg = error_data.get("message", "")
            
            if isinstance(raw_msg, list):
                message = "; ".join(map(str, raw_msg))
            else:
                message = str(raw_msg)
                
            if not message or message == "[object Object]":
                message = await response.text()
        except Exception:
            message = await response.text()
            
        return {"error": True, "status": response.status, "message": message}

    async def _request(self, method: str, path: str, **kwargs):
        async with aiohttp.ClientSession() as session:
            url = f"{self.base_url}{path}"
            headers = kwargs.pop("headers", {})
            async with session.request(method, url, headers=headers, **kwargs) as response:
                if response.status >= 400:
                    return await self._handle_error(response)
                return await response.json()

    def _admin_payload(self, admin_id: int, extra: dict = None) -> dict:
        payload = {"adminId": str(admin_id)}
        if extra:
            payload.update(extra)
        return payload
