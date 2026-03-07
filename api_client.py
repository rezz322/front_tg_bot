import aiohttp
from config import API_BASE_URL

class BackendAPI:
    def __init__(self, base_url: str = API_BASE_URL):
        self.base_url = base_url

    async def _request(self, method: str, path: str, **kwargs):
        async with aiohttp.ClientSession() as session:
            url = f"{self.base_url}{path}"
            headers = kwargs.pop("headers", {})
            async with session.request(method, url, headers=headers, **kwargs) as response:
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

    async def list_accounts(self, admin_id: int):
        adm_id = int(str(admin_id)) if str(admin_id).isdigit() else admin_id
        return await self._request("GET", "/accounts", params={"adminId": adm_id})

    # GET /accounts/user/{telegram_id}
    async def get_user_accounts(self, telegram_id: int):
        return await self._request("GET", f"/accounts/user/{telegram_id}")

    # POST /accounts/admin/give-key
    async def give_key(self, target_id: str, number: str, admin_id: int, days: int = None):
        adm_id_int = int(str(admin_id))
        adm_id_str = str(admin_id)
        payload = {
            "telegramId": str(target_id),
            "adminId": adm_id_str,
            "phone": str(number),
            "days": days
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

    # POST /users/admin/info/username
    async def get_user_info_by_username(self, username: str, admin_id: int):
        payload = {
            "username": str(username),
            "adminId": str(admin_id)
        }
        return await self._request("POST", "/users/admin/info/username", json=payload)

    # POST /users/admin/ban/username
    async def ban_user_by_username(self, username: str, admin_id: int):
        payload = {
            "username": str(username),
            "adminId": str(admin_id)
        }
        return await self._request("POST", "/users/admin/ban/username", json=payload)

    # POST /users/admin/whitelist
    async def toggle_whitelist(self, target_id: str, admin_id: int):
        payload = {
            "telegramId": str(target_id),
            "adminId": str(admin_id)
        }
        return await self._request("POST", "/users/admin/whitelist", json=payload)

    # POST /users/admin/whitelist/username
    async def toggle_whitelist_by_username(self, username: str, admin_id: int):
        payload = {
            "username": str(username),
            "adminId": str(admin_id)
        }
        return await self._request("POST", "/users/admin/whitelist/username", json=payload)

    # POST /accounts/admin/give-key/username
    async def give_key_by_username(self, username: str, phone: str, admin_id: int, days: int = None):
        payload = {
            "username": username,
            "phone": phone,
            "adminId": str(admin_id),
            "days": days
        }
        return await self._request("POST", "/accounts/admin/give-key/username", json=payload)

    # POST /accounts/auto-issue
    async def auto_issue_key(self, user_id: int, full_name: str, phone: str, pin: str):
        payload = {
            "telegramId": str(user_id),
            "fullName": full_name,
            "phone": phone,
            "pin": pin
        }
        return await self._request("POST", "/accounts/auto-issue", json=payload)

    # PATCH /accounts/{id}
    async def update_account(self, account_id: int, data: dict, admin_id: int):
        # We pass adminId in query for security check if backend requires it, 
        # but Patch usually takes data in body. Backend controller uses @Body() data: Prisma.AccountUpdateInput
        # We need to ensure admin check is done (usually via middleware or logic in controller)
        return await self._request("PATCH", f"/accounts/{account_id}", params={"adminId": admin_id}, json=data)

    # POST /accounts/admin/take-away/{id}
    async def take_away_account(self, account_id: int, admin_id: int):
        return await self._request("POST", f"/accounts/admin/take-away/{account_id}", json={"adminId": str(admin_id)})

    # POST /accounts/admin/toggle-ban/{id}
    async def toggle_account_ban(self, account_id: int, admin_id: int):
        return await self._request("POST", f"/accounts/admin/toggle-ban/{account_id}", json={"adminId": str(admin_id)})

backend_api = BackendAPI()
