import aiohttp
from config import API_BASE_URL

class BaseAPI:
    def __init__(self, base_url: str = API_BASE_URL, session: aiohttp.ClientSession = None):
        self.base_url = base_url
        self._session = session
        self._own_session = False

    async def _get_session(self) -> aiohttp.ClientSession:
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession()
            self._own_session = True
        return self._session

    async def close(self):
        if self._own_session and self._session and not self._session.closed:
            await self._session.close()

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
        session = await self._get_session()
        url = f"{self.base_url.rstrip('/')}/{path.lstrip('/')}"
        headers = kwargs.pop("headers", {})
        
        try:
            async with session.request(method, url, headers=headers, **kwargs) as response:
                if response.status >= 400:
                    return await self._handle_error(response)
                return await response.json()
        except Exception as e:
            return {"error": True, "status": 500, "message": f"Connection error: {str(e)}"}

    def _admin_payload(self, admin_id: int, extra: dict = None) -> dict:
        payload = {"adminId": str(admin_id)}
        print(extra)
        if extra:
            payload.update(extra)
        return payload
