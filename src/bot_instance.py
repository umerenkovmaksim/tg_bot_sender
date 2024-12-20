import logging

from aiogram import Bot, Dispatcher
from config.settings import BOT_TOKEN


bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
logging.basicConfig(level=logging.INFO)

