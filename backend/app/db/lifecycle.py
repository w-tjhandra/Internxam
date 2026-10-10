import asyncpg

from app.db.schema import initialize_schema, seed_initial_data


async def open_database(dsn: str):
    pool = await asyncpg.create_pool(dsn)
    try:
        await initialize_schema(pool)
        await seed_initial_data(pool)
    except Exception:
        await pool.close()
        raise
    return pool


async def close_database(pool) -> None:
    await pool.close()
