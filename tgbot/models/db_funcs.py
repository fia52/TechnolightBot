from typing import Union

import asyncpg
from asyncpg import UniqueViolationError
from asyncpg import Pool, Connection
from tgbot.config import load_config

config = load_config(".env")


class Database:
    def __init__(self):
        self.pool: Union[Pool, None] = None

    async def create(self):
        self.pool = await asyncpg.create_pool(
            user=config.db.user,
            password=config.db.password,
            host=config.db.host,
            port=config.db.port,
            database=config.db.database,
        )

    async def execute(
        self,
        command,
        *args,
        fetch: bool = False,
        fetchval: bool = False,
        fetchrow: bool = False,
        execute: bool = False,
    ):
        async with self.pool.acquire() as connection:
            connection: Connection
            async with connection.transaction():
                if fetch:
                    result = await connection.fetch(command, *args)
                elif fetchval:
                    result = await connection.fetchval(command, *args)
                elif fetchrow:
                    result = await connection.fetchrow(command, *args)
                elif execute:
                    result = await connection.execute(command, *args)
            return result

    async def create_table_users(self):
        sql = """
        CREATE TABLE IF NOT EXISTS users (
        fio VARCHAR(255) NOT NULL,
        phone_number VARCHAR(50) NOT NULL,
        position VARCHAR(255) NOT NULL,
        unique_code VARCHAR(100) NOT NULL,
        telegram_id VARCHAR(50)
        );
        """
        await self.execute(sql, execute=True)

    async def create_table_search_history(self):
        sql = """
        CREATE TABLE IF NOT EXISTS search_history 
        (user_id VARCHAR(50), 
        searched_code VARCHAR(255), 
        search_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP);
        """
        await self.execute(sql, execute=True)

    async def add_user(
        self,
        fio: str,
        phone_number: str,
        position: str,
        unique_code: str,
        telegram_id: str,
    ):
        try:
            sql = """
            INSERT INTO users (fio, phone_number, position, unique_code, telegram_id)
            VALUES ($1, $2, $3, $4, $5)
            """
            return await self.execute(
                sql, fio, phone_number, position, unique_code, telegram_id, execute=True
            )
        except UniqueViolationError:
            pass

    async def add_to_search_history(self, telegram_id: str, code: str):
        sql = """
        INSERT INTO search_history (user_id, searched_code)
        VALUES ($1, $2)
        """
        return await self.execute(sql, telegram_id, code, execute=True)

    async def get_search_history(self, telegram_id: str):
        sql = """
        SELECT searched_code, search_time  
        FROM search_history 
        WHERE user_id = $1
        ORDER BY search_time DESC
        """
        res = await self.execute(sql, telegram_id, fetch=True)
        return [x.get("searched_code") for x in res]

    async def get_user_by_code(self, code: str):
        sql = """
        SELECT *  
        FROM users 
        WHERE unique_code = $1
        """
        res = await self.execute(sql, code, fetchrow=True)
        return res

    async def get_user_by_telegram_id(self, telegram_id: str):
        sql = f"""
        SELECT *  
        FROM users 
        WHERE telegram_id = $1
        """
        res = await self.execute(sql, telegram_id, fetchrow=True)
        return res


async def on_startup(db: Database):
    await db.create()
    await db.create_table_users()
    await db.create_table_search_history()
    print("connection to postgres done")
