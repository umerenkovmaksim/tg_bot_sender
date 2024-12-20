import asyncio
import uvicorn

from aiogram import F, BaseMiddleware, types
from aiogram.filters import Command

from bot_instance import bot, dp
from database import get_or_create_user, create_table
from fastapi_app.app import app as fastapi_app
from handlers.admin_handlers import router as admin_router
from keyboards import build_service_auth_kb, subscribe_check_kb
from config.messages import *
from config.settings import CHANNEL_ID


class CheckReqsMiddleware(BaseMiddleware):
    async def __call__(self, handler, event: types.Message | types.CallbackQuery, data: dict):
        user_id = event.from_user.id
        if isinstance(event, types.CallbackQuery):
            await event.message.delete()
        member = await bot.get_chat_member(CHANNEL_ID, user_id)
        if member.status not in ['member', 'administrator', 'creator']:
            await bot.send_message(
                user_id,
                text=HELLO_MESSAGE_WITHOUT_CHANNELS,
                reply_markup=subscribe_check_kb.as_markup(),
            )
            return

        user = await get_or_create_user(telegram_id=user_id)

        if not user[1]:
            kb = await build_service_auth_kb(user_id)
            await bot.send_message(
                user_id,
                text=SERVICE_DATA_WAIT_MESSAGE,
                reply_markup=kb.as_markup(),
            )
        return await handler(event, data)


dp.include_router(admin_router)

dp.message.middleware(CheckReqsMiddleware())
dp.callback_query.middleware(CheckReqsMiddleware())


@dp.message(Command('start'))
async def start_message(message: types.Message):
    await bot.send_message(message.from_user.id, text=SUCCESS_MESSAGE)


@dp.callback_query(F.data == 'check')
async def callback_check(query: types.CallbackQuery):
    await bot.send_message(query.from_user.id, text=SUCCESS_MESSAGE)


async def create_postback(user_id):
    return True


async def run_bot():
    await create_table()
    await dp.start_polling(bot)


async def run_fastapi():
    config = uvicorn.Config(app=fastapi_app, host='0.0.0.0', port=8040)
    server = uvicorn.Server(config)
    await server.serve()


async def main():
    bot_task = asyncio.create_task(run_bot())
    fastapi_task = asyncio.create_task(run_fastapi())

    await asyncio.gather(bot_task, fastapi_task)


if __name__ == "__main__":
    asyncio.run(main())
