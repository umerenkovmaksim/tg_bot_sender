from aiogram.utils.keyboard import InlineKeyboardBuilder, InlineKeyboardButton
from config.settings import BUTTON_URL
from config.messages import AUTH_BUTTON, AUTH_CHECK_BUTTON, SUBSCRIBE_CHECK_BUTTON


async def build_service_auth_kb(telegram_id):
    api_url = BUTTON_URL + '/' if BUTTON_URL[-1] != '/' else ''
    url = f"{api_url}confirm_user?telegram_id={telegram_id}"
    kb = InlineKeyboardBuilder()
    kb.add(InlineKeyboardButton(
        text=AUTH_BUTTON,
        url=url,
    ))
    kb.add(InlineKeyboardButton(
        text=AUTH_CHECK_BUTTON,
        callback_data='check',
    ))

    return kb

subscribe_check_kb = InlineKeyboardBuilder()
subscribe_check_kb.add(InlineKeyboardButton(
    text=SUBSCRIBE_CHECK_BUTTON,
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