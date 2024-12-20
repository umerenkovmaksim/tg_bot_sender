import asyncio

import aiosqlite
from contextlib import asynccontextmanager

from config.settings import DATABASE_URL


@asynccontextmanager
async def get_db():
    conn = await aiosqlite.connect(DATABASE_URL)
    try:
        yield conn
    finally:
        await conn.close()


async def create_table():
    async with get_db() as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                telegram_id INTEGER PRIMARY KEY,
                is_active INTEGER DEFAULT 0,
                is_admin INTEGER DEFAULT 0
            );
        """)
        await db.commit()


async def get_user_by_telegram_id(telegram_id):
    async with get_db() as db:
        cursor = await db.execute("SELECT * FROM users WHERE telegram_id=?", (telegram_id,))
        user = await cursor.fetchone()

        return user


async def create_user(telegram_id):
    async with get_db() as db:
        cursor = await db.execute("INSERT INTO users (telegram_id) VALUES (?)", (telegram_id,))
        await db.commit()
        last_row_id = cursor.lastrowid
        cursor = await cursor.execute("SELECT * FROM users WHERE telegram_id=?", (last_row_id,))

        return await cursor.fetchone()


async def get_or_create_user(telegram_id):
    if user := await get_user_by_telegram_id(telegram_id):
        return user
    user = await create_user(telegram_id)

    return user


async def set_user_active(telegram_id, is_active=True):
    async with get_db() as db:
        await db.execute(
            "UPDATE users SET is_active=? WHERE telegram_id=?",
            (is_active, telegram_id,),
        )
        cursor = await db.execute("SELECT * FROM users WHERE telegram_id = ?", (telegram_id,))
        updated_user = await cursor.fetchone()
        await db.commit()
        return updated_user


async def set_admin(telegram_id, is_admin=True):
    async with get_db() as db:
        await db.execute(
            "UPDATE users SET is_admin=? WHERE telegram_id=?",
            (is_admin, telegram_id,),
        )
        cursor = await db.execute("SELECT * FROM users WHERE telegram_id = ?", (telegram_id,))
        updated_user = await cursor.fetchone()
        await db.commit()
        return updated_user
    

async def get_all_users():
    async with get_db() as db:
        cursor = await db.execute(
            "SELECT * FROM users"
        )
        users = await cursor.fetchall()
        return users
