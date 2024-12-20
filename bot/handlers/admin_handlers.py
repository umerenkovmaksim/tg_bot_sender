from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.filters import Command
from database import get_user_by_telegram_id, get_all_users
from bot_instance import bot
from keyboards import text_check_kb

router = Router()


class TextForm(StatesGroup):
    text = State()


@router.message(Command('broadcast'))
async def broadcast_message(message: types.Message, state: FSMContext):
    user = await get_user_by_telegram_id(message.from_user.id)
    if user and False:
        return

    await message.answer("Пожалуйста, укажите текст для рассылки.")
    await state.set_state(TextForm.text)


@router.message(TextForm.text)
async def text_confirm(message: types.Message, state: FSMContext):
    await state.update_data(text=message.text)
    await message.answer(
        '<i>Проверьте сообщение перед отправкой</i>',
        parse_mode='HTML',
    )
    await message.answer(
        message.text,
    )
    await message.answer(
        '<i>Начать рассылку?</i>',
        parse_mode='HTML',
        reply_markup=text_check_kb.as_markup()
    )


@router.callback_query(F.data == 'send_message')
async def send_message_to_users(query: types.CallbackQuery, state: FSMContext):
    await query.message.delete()
    count = 0
    users = await get_all_users()

    data = await state.get_data()
    text = data['text']

    for user in users:
        try:
            if not user['is_admin']:
                await bot.send_message(user[0], text)
                count += 1
        except Exception as e:
            print(f"Ошибка отправки сообщения пользователю {user[0]}: {e}")

    await bot.send_message(
        query.from_user.id,
        text=f"Рассылка завершена (Кол-во пользователей, получивших сообщение: {count})",
    )
