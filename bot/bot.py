import os
import sys
import asyncio

from aiogram import F, BaseMiddleware, types
from aiogram.filters import Command
from typing import Union

parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

if parent_dir not in sys.path:
    sys.path.append(parent_dir)

from bot_instance import bot, dp
from database import get_or_create_user, create_table, init_admins
from handlers.admin_handlers import router as admin_router
from keyboards import build_service_auth_kb, subscribe_check_kb
from config.messages import *
from config.settings import CHANNEL_IDS, ADMIN_IDS


class CheckReqsMiddleware(BaseMiddleware):
    async def __call__(self, handler, event: Union[types.Message, types.CallbackQuery], data: dict):
        user_id = event.from_user.id
        if user_id in ADMIN_IDS:
            return await handler(event, data)
        text = HELLO_MESSAGE_WITHOUT_CHANNELS
        completed = True
        for channel_id in CHANNEL_IDS:
            member = await bot.get_chat_member(channel_id, user_id)
            if member.status not in ['member', 'administrator', 'creator']:
                completed = False
                text += f'\n❌ {channel_id}'
            else:
                text += f'\n✅ {channel_id}'
        if not completed:
            await bot.send_message(
                user_id,
                text=text,
                reply_markup=subscribe_check_kb.as_markup(),
            )
            return
        
        user = await get_or_create_user(telegram_id=user_id)

        if not user['is_active']:
            kb = await build_service_auth_kb(user_id)
            await bot.send_message(
                user_id,
                text=SERVICE_DATA_WAIT_MESSAGE,
                reply_markup=kb.as_markup(),
            )
            return
        return await handler(event, data)


dp.include_router(admin_router)

dp.message.middleware(CheckReqsMiddleware())
dp.callback_query.middleware(CheckReqsMiddleware())


@dp.message(Command('start'))
async def start_message(message: types.Message):
    await bot.send_message(message.from_user.id, text=SUCCESS_MESSAGE)


@dp.callback_query(F.data == 'check')
async def callback_check(query: types.CallbackQuery):
    await query.message.delete()
    await bot.send_message(query.from_user.id, text=SUCCESS_MESSAGE)


async def main():
    await init_admins()
    await create_table()
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
