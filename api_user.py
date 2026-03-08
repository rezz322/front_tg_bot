from api_base import BaseAPI

class UserAPI(BaseAPI):

    async def check_admin(self, user_id: int):
        return await self._request("GET", f"/users/check-admin/{user_id}")

    async def check_access(self, user_id: int, username: str = None):
        params = {}
        if username:
            params["username"] = username
        return await self._request("GET", f"/users/check-access/{user_id}", params=params)

    async def get_user_by_id(self, user_id: int):
        return await self._request("GET", f"/users/{user_id}")

    async def get_user_accounts(self, telegram_id: int):
        return await self._request("GET", f"/accounts/user/{telegram_id}")

    async def get_available_accounts(self):
        return await self._request("GET", "/accounts/get-available-accounts")

    async def get_client_apk(self):
        return await self._request("GET", "/bot/client-apk")

    async def get_admin_apk(self):
        return await self._request("GET", "/bot/admin-apk")

    async def check_ban_by_number(self, number: str):
        return await self._request("GET", f"/accounts/check-ban/{number}")

    async def check_ban_by_key(self, key: str):
        return await self._request("GET", f"/accounts/key-check-ban/{key}")

    async def auto_issue_key(self, user_id: int, phone: str, pin: str):
        payload = {
            "telegramId": str(user_id),
            "phone": phone,
            "pin": pin
        }
        return await self._request("POST", "/accounts/auto-issue", json=payload)

user_api = UserAPI()
