import aiomysql
from contextlib import asynccontextmanager

from config.settings import DB_HOST, DB_PORT, DB_USER, DB_PASSWORD, DB_NAME, ADMIN_IDS


@asynccontextmanager
async def get_db():
    conn = await aiomysql.connect(
        host=DB_HOST,
        port=DB_PORT,
        user=DB_USER,
        password=DB_PASSWORD,
        db=DB_NAME,
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


async def init_admins():
    async with get_db() as db:
        await db.execute("UPDATE users SET is_admin = %s", (False,))
        for telegram_id in ADMIN_IDS:
            cursor = await db.execute("SELECT is_admin FROM users WHERE telegram_id = %s", (telegram_id,))
            admin = await cursor.fetchone()
            if not admin:
                await cursor.execute(
                    "INSERT INTO users (telegram_id, is_active, is_admin) VALUES (%s, %s, %s)",
                    (telegram_id, True, True)
                )
            elif not admin[0]:
                await cursor.execute(
                    "UPDATE users SET is_admin = %s WHERE telegram_id = %s",
                    (True, telegram_id)
                )


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
