import asyncio
import logging
import sys
from aiogram import Bot, Dispatcher
from config import BOT_TOKEN, ADMIN_IDS
from handlers import base, admin, user
from middlewares import BanMiddleware
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import uvicorn



app = FastAPI()
bot = Bot(token=BOT_TOKEN)

@app.post("/notify/account_created")
async def notify_account_created(request: Request):
    data = await request.json()
    pin = data.get("pin")
    full_name = data.get("full_name")
    phone = data.get("phone")

    if not all([pin, full_name, phone]):
        return JSONResponse(content={"error": "Missing required fields"}, status_code=400)

    message = (
        f"🆕 <b>Создан новый аккаунт!</b>\n\n"
        f"👤 <b>ФИО:</b> {full_name}\n"
        f"📞 <b>Номер:</b> {phone}\n"
        f"🔑 <b>Пин-код:</b> {pin}"
    )

    for admin_id in ADMIN_IDS:
        try:
            await bot.send_message(admin_id, message, parse_mode="HTML")
            logging.info(f"Notification sent to admin {admin_id}")
        except Exception as e:
            logging.error(f"Failed to send notification to admin {admin_id}: {e}")

    return {"status": "success"}


async def run_bot():

    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()
    dp.message.middleware(BanMiddleware())
    dp.callback_query.middleware(BanMiddleware())

    dp.include_router(base.router)
    dp.include_router(admin.router)
    dp.include_router(user.router)

    logging.info("Starting bot...")
    await dp.start_polling(bot)


async def run_api():
    config = uvicorn.Config(app, host="0.0.0.0", port=8000)
    server = uvicorn.Server(config)
    await server.serve()


async def main():
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    await asyncio.gather(run_bot(), run_api())

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
