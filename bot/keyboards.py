from aiogram.utils.keyboard import InlineKeyboardBuilder, InlineKeyboardButton
from config.settings import API_URL


async def build_service_auth_kb(telegram_id):
    url = f"{API_URL}/confirm_user?telegram_id={telegram_id}"
    kb = InlineKeyboardBuilder()
    kb.add(InlineKeyboardButton(
        text='Авторизация',
        url=url,
    ))
    kb.add(InlineKeyboardButton(
        text='Проверить авторизацию',
        callback_data='check',
    ))

    return kb

subscribe_check_kb = InlineKeyboardBuilder()
subscribe_check_kb.add(InlineKeyboardButton(
    text='Проверить подписку',
    callback_data='check',
))

text_check_kb = InlineKeyboardBuilder()
text_check_kb.add(InlineKeyboardButton(
    text='Да',
    callback_data='send_message'
))
text_check_kb.add(InlineKeyboardButton(
    text='Нет',
    callback_data='cancel_send_message'
))