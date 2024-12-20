import os
import asyncpg
from contextlib import asynccontextmanager

DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://postgres:postgres@localhost:5432/postgres')


@asynccontextmanager
async def get_db():
    conn = await asyncpg.connect(DATABASE_URL)
    try:
        yield conn
    finally:
        await conn.close()


async def create_table():
    async with get_db() as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                telegram_id BIGINT PRIMARY KEY,
                is_active BOOLEAN DEFAULT FALSE,
                is_admin BOOLEAN DEFAULT FALSE
            );
        """)


async def get_user_by_telegram_id(telegram_id):
    async with get_db() as db:
        user = await db.fetchrow("SELECT * FROM users WHERE telegram_id = $1", telegram_id)
        return dict(user) if user else None


async def create_user(telegram_id):
    async with get_db() as db:
        await db.execute("INSERT INTO users (telegram_id) VALUES ($1)", telegram_id)
        user = await db.fetchrow("SELECT * FROM users WHERE telegram_id = $1", telegram_id)
        return dict(user)


async def get_or_create_user(telegram_id):
    user = await get_user_by_telegram_id(telegram_id)
    if user:
        return user
    return await create_user(telegram_id)


async def set_user_active(telegram_id, is_active=True):
    async with get_db() as db:
        await db.execute(
            "UPDATE users SET is_active = $1 WHERE telegram_id = $2",
            is_active, telegram_id,
        )
        updated_user = await db.fetchrow("SELECT * FROM users WHERE telegram_id = $1", telegram_id)
        return dict(updated_user) if updated_user else None


async def set_admin(telegram_id, is_admin=True):
    async with get_db() as db:
        await db.execute(
            "UPDATE users SET is_admin = $1 WHERE telegram_id = $2",
            is_admin, telegram_id,
        )
        updated_user = await db.fetchrow("SELECT * FROM users WHERE telegram_id = $1", telegram_id)
        return dict(updated_user) if updated_user else None


async def get_all_users():
    async with get_db() as db:
        users = await db.fetch("SELECT * FROM users")
        return [dict(user) for user in users]
