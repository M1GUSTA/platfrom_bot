from typing import Union

import asyncpg
from asyncpg import Pool, Connection

from tgbot.config import Config, load_config


class Database:
    def __init__(self):
        self.pool: Union[Pool, None] = None

    async def create(self):
        config: Config = load_config()
        self.pool = await asyncpg.create_pool(
                user=config.db.user,
                password=config.db.password,
                host=config.db.host,
                database=config.db.database
        )

    async def execute(self, command, *args,
                      fetch: bool = False,
                      fetchval: bool = False,
                      fetchrow: bool = False,
                      execute: bool = False
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

    @staticmethod
    def format_args(sql, parameters: dict):
        sql += " AND ".join([
            f"{item} = ${num}" for num, item in enumerate(parameters.keys(),
                                                          start=1)
        ])
        return sql, tuple(parameters.values())


    async def add_admin(self, telegram_id, full_name, username):
        sql = "INSERT INTO admin (full_name, username, telegram_id) VALUES($1, $2, $3) returning *"
        return await self.execute(sql, full_name, username, telegram_id, fetchrow=True)

    async def select_all_admins(self):
        sql = "SELECT * FROM admin"
        return await self.execute(sql, fetch=True)

    async def select_user(self, **kwargs):
        sql = "SELECT * FROM users WHERE "
        sql, parameters = self.format_args(sql, parameters=kwargs)
        return await self.execute(sql, *parameters, fetchrow=True)

    async def add_proffer(self, **kwargs):
        sql = "INSERT INTO proffer(content, anon, id_user, id_status, title) VALUES($1, $2, $3, $4, $5) returning *"
        return await self.execute(sql, kwargs, fetchrow=True)




