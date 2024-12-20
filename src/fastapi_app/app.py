from fastapi import FastAPI

from database import set_user_active

app = FastAPI()


@app.get('confirm_user')
async def confirm_user(telegram_id):
    await set_user_active(telegram_id, True)

