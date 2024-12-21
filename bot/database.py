import aiomysql
from contextlib import asynccontextmanager


@asynccontextmanager
async def get_db():
    conn = await aiomysql.connect(
        host='localhost',
        port=3306,
        user='u2948470_default',
        password='JjWs1WV28JIh93Lw',
        db='u2948470_default',
    )
    try:
        async with conn.cursor(aiomysql.DictCursor) as cursor:
            yield cursor
        await conn.commit()
    finally:
        conn.close()


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
        await db.execute("SELECT * FROM users WHERE telegram_id = %s", (telegram_id,))
        user = await db.fetchone()
        return user if user else None


async def create_user(telegram_id):
    async with get_db() as db:
        await db.execute("INSERT INTO users (telegram_id) VALUES (%s)", (telegram_id,))
        await db.execute("SELECT * FROM users WHERE telegram_id = %s", (telegram_id,))
        user = await db.fetchone()
        return user


async def get_or_create_user(telegram_id):
    user = await get_user_by_telegram_id(telegram_id)
    if user:
        return user
    return await create_user(telegram_id)


async def set_user_active(telegram_id, is_active=True):
    async with get_db() as db:
        await db.execute(
            "UPDATE users SET is_active = %s WHERE telegram_id = %s",
            (is_active, telegram_id)
        )
        await db.execute("SELECT * FROM users WHERE telegram_id = %s", (telegram_id,))
        updated_user = await db.fetchone()
        return updated_user if updated_user else None


async def set_admin(telegram_id, is_admin=True):
    async with get_db() as db:
        await db.execute(
            "UPDATE users SET is_admin = %s WHERE telegram_id = %s",
            (is_admin, telegram_id)
        )
        await db.execute("SELECT * FROM users WHERE telegram_id = %s", (telegram_id,))
        updated_user = await db.fetchone()
        return updated_user if updated_user else None


async def get_all_users():
    async with get_db() as db:
        await db.execute("SELECT * FROM users")
        users = await db.fetchall()
        return users
