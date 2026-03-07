import aiohttp
from config import API_BASE_URL

class BackendAPI:
    def __init__(self, base_url: str = API_BASE_URL):
        self.base_url = base_url

    async def _request(self, method: str, path: str, **kwargs):
        async with aiohttp.ClientSession() as session:
            url = f"{self.base_url}{path}"
            async with session.request(method, url, **kwargs) as response:
                if response.status >= 400:
                    text = await response.text()
                    return {"error": True, "status": response.status, "message": text}
                return await response.json()

    # POST /users
    async def register_user(self, user_data: dict):
        # Based on TelegramUsersController, it expects { "id": "string", "username": "string" }
        payload = {
            "id": str(user_data["id"]),
            "username": user_data.get("username", "unknown")
        }
        return await self._request("POST", "/users", json=payload)

    # GET /users
    async def list_users(self, admin_id: int):
        adm_id_int = int(str(admin_id))
        return await self._request("GET", "/users", params={"adminId": adm_id_int})

    # GET /bot/check-admin/{user_id}
    async def check_admin(self, user_id: int):
        return await self._request("GET", f"/bot/check-admin/{user_id}")

    # GET /users/{user_id}
    async def get_user_by_id(self, user_id: int):
        return await self._request("GET", f"/users/{user_id}")

    # POST /users/admin/info
    async def get_user_info(self, target_id: str, admin_id: int):
        # Using pure integers in Body if string fails, but trying string first as per controller
        # However, many Prisma setups prefer numbers. Let's try strings as per your snippet.
        payload = {
            "telegramId": str(target_id),
            "adminId": str(admin_id)
        }
        return await self._request("POST", "/users/admin/info", params={"adminId": int(admin_id)}, json=payload)

    # POST /users/admin/ban
    async def ban_user(self, target_id: str, admin_id: int):
        payload = {
            "telegramId": str(target_id),
            "adminId": str(admin_id)
        }
        return await self._request("POST", "/users/admin/ban", params={"adminId": int(admin_id)}, json=payload)

    # GET /accounts
    async def list_accounts(self, admin_id: int):
        adm_id = int(str(admin_id)) if str(admin_id).isdigit() else admin_id
        return await self._request("GET", "/accounts", params={"adminId": adm_id})

    # POST /accounts/admin/give-key
    async def give_key(self, target_id: str, number: str, admin_id: int):
        adm_id_int = int(str(admin_id))
        adm_id_str = str(admin_id)
        payload = {
            "telegramId": str(target_id),
            "adminId": adm_id_str,
            "phone": str(number)
        }
        return await self._request("POST", "/accounts/admin/give-key", params={"adminId": adm_id_int}, json=payload)

    # POST /accounts/admin/info/{number}
    async def get_account_info(self, number: str, admin_id: int):
        adm_id_int = int(str(admin_id))
        adm_id_str = str(admin_id)
        return await self._request("POST", f"/accounts/admin/info/{number}", params={"adminId": adm_id_int}, json={"adminId": adm_id_str})

    # POST /accounts/admin/refresh/{number}
    async def refresh_account_key(self, number: str, admin_id: int):
        adm_id_int = int(str(admin_id))
        adm_id_str = str(admin_id)
        return await self._request("POST", f"/accounts/admin/refresh/{number}", params={"adminId": adm_id_int}, json={"adminId": adm_id_str})

    # GET /accounts/get-available-accounts
    async def get_available_accounts(self):
        return await self._request("GET", "/accounts/get-available-accounts")

    # GET /bot/client-apk
    async def get_client_apk(self):
        return await self._request("GET", "/bot/client-apk")

    # GET /bot/admin-apk
    async def get_admin_apk(self):
        return await self._request("GET", "/bot/admin-apk")

    # POST /users/admin/unban (Using toggleBan at admin/ban)
    async def unban_user(self, target_id: str, admin_id: int):
        payload = {
            "telegramId": str(target_id),
            "adminId": str(admin_id)
        }
        return await self._request("POST", "/users/admin/ban", params={"adminId": int(admin_id)}, json=payload)

    # GET /accounts/check-ban/:number
    async def check_ban_by_number(self, number: str):
        return await self._request("GET", f"/accounts/check-ban/{number}")

    # GET /accounts/key-check-ban/:key
    async def check_ban_by_key(self, key: str):
        return await self._request("GET", f"/accounts/key-check-ban/{key}")

backend_api = BackendAPI()
