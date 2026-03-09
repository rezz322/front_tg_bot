from api_base import BaseAPI

class AdminAPI(BaseAPI):
    async def list_users(self, admin_id: int):
        return await self._request("GET", "/users", params={"adminId": int(admin_id)})

    async def toggle_user_ban(self, target_id: str, admin_id: int):
        return await self._request("POST", f"/users/admin/ban/{target_id}", json={"adminId": str(admin_id)})

    async def list_accounts(self, admin_id: int):
        return await self._request("GET", "/accounts", params={"adminId": admin_id})

    async def get_user_accounts(self, target_id: int, admin_id: int):
        return await self._request("GET", f"/accounts/user/{target_id}", params={"adminId": admin_id})

    async def give_key(self, target_id: str, number: str, admin_id: int, days: int = None):
        payload = self._admin_payload(admin_id, {"telegramId": str(target_id), "phone": str(number), "days": days})
        return await self._request("POST", "/accounts/admin/give-key", params={"adminId": int(admin_id)}, json=payload)

    async def get_account_info(self, number: str, admin_id: int):
        return await self._request("POST", f"/accounts/admin/info/{number}", params={"adminId": int(admin_id)}, json={"adminId": str(admin_id)})

    async def refresh_account_key(self, number: str, admin_id: int):
        return await self._request("POST", f"/accounts/admin/refresh/{number}", params={"adminId": int(admin_id)}, json={"adminId": str(admin_id)})

    async def get_user_info_by_username(self, username: str, admin_id: int):
        payload = self._admin_payload(admin_id, {"username": str(username)})
        return await self._request("POST", "/users/admin/info/username", json=payload)

    async def ban_user_by_username(self, username: str, admin_id: int):
        payload = self._admin_payload(admin_id, {"username": str(username)})
        return await self._request("POST", "/users/admin/ban/username", json=payload)

    async def toggle_whitelist(self, target_id: str, admin_id: int):
        payload = self._admin_payload(admin_id, {"telegramId": str(target_id)})
        return await self._request("POST", "/users/admin/whitelist", json=payload)

    async def toggle_whitelist_by_username(self, username: str, admin_id: int):
        payload = self._admin_payload(admin_id, {"username": str(username)})
        return await self._request("POST", "/users/admin/whitelist/username", json=payload)

    async def give_key_by_username(self, username: str, phone: str, admin_id: int, days: int = None):
        payload = self._admin_payload(admin_id, {"username": username, "phone": phone, "days": days})
        return await self._request("POST", "/accounts/admin/give-key/username", json=payload)

    async def update_account(self, account_id: str, data: dict, admin_id: int):
        return await self._request("PATCH", f"/accounts/{account_id}", params={"adminId": admin_id}, json=data)

    async def take_away_account(self, account_id: str, admin_id: int):
        return await self._request("POST", f"/accounts/admin/take-away/{account_id}", json={"adminId": str(admin_id)})

    async def toggle_account_ban(self, account_id: str, admin_id: int):
        return await self._request("POST", f"/accounts/admin/toggle-ban/{account_id}", json={"adminId": str(admin_id)})

    async def remove_account_from_user(self, phone: str, identifier: str, admin_id: int):
        payload = {
            "phone": phone,
            "identifier": str(identifier),
            "adminId": str(admin_id)
        }
        return await self._request("DELETE", "/accounts/admin/remove-account", json=payload)

    async def set_user_limit(self, target_id: str, limit: int, admin_id: int):
        return await self._request("PATCH", f"/users/admin/limit/{target_id}", json={"limit": int(limit), "adminId": str(admin_id)})

admin_api = AdminAPI()
