from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.filters import Command
from database import get_user_by_telegram_id, get_all_users
from bot_instance import bot
from keyboards import text_check_kb
from config.messages import BEFORE_BROADCAST_TEXT, MESSAGE_CHECK_TEXT, START_BROADCAST_TEXT

router = Router()


class TextForm(StatesGroup):
    chat_id = State()
    message_id = State()


@router.message(Command('message'))
async def broadcast_message(message: types.Message, state: FSMContext):
    user = await get_user_by_telegram_id(message.from_user.id)
    if user and user['is_admin']:
        return

    await message.answer(BEFORE_BROADCAST_TEXT)
    await state.set_state(TextForm.message_id)


@router.message(TextForm.message_id)
async def text_confirm(message: types.Message, state: FSMContext):
    await state.update_data(
        message_id=message.message_id, 
        chat_id=message.from_user.id,
    )
    await message.answer(
        MESSAGE_CHECK_TEXT,
        parse_mode='HTML',
    )
    await bot.copy_message(
        chat_id=message.from_user.id,
        from_chat_id=message.from_user.id,
        message_id=message.message_id,
    )
    await message.answer(
        START_BROADCAST_TEXT,
        parse_mode='HTML',
        reply_markup=text_check_kb.as_markup()
    )


@router.callback_query(F.data == 'send_message')
async def send_message_to_users(query: types.CallbackQuery, state: FSMContext):
    await query.message.delete()
    count = 0
    users = await get_all_users()

    data = await state.get_data()

    for user in users:
        try:
            if not user.get('is_admin'):
                await bot.copy_message(
                    chat_id=user.get('telegram_id'),
                    from_chat_id=data.get('chat_id'),
                    message_id=data.get('message_id'),
                )
                count += 1
        except Exception as e:
            print(f"Ошибка отправки сообщения пользователю {user.get('telegram_id')}: {e}")

    await bot.send_message(
        query.from_user.id,
        text=f"Рассылка завершена (Кол-во пользователей, получивших сообщение: {count})",
    )
