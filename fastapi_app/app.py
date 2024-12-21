import os
import sys
from fastapi import FastAPI

parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

if parent_dir not in sys.path:
    sys.path.append(parent_dir)

from database import set_user_active

app = FastAPI()


@app.get('/confirm_user')
async def confirm_user(telegram_id):
    telegram_id = int(telegram_id)
    await set_user_active(telegram_id, True)

