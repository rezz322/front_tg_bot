from aiogram import Router
from .admin_users import router as users_router
from .admin_accounts import router as accounts_router
from .admin_apks import router as apks_router

router = Router()

# Aggregate all admin sub-routers
router.include_router(users_router)
router.include_router(accounts_router)
router.include_router(apks_router)
