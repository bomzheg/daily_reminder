from typing import Callable, Dict, Any, Awaitable

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject
from sqlalchemy.orm import sessionmaker

from app.dao.holder import HolderDao
from app.mapper import user_mapper, chat_mapper
from app.services.chat import upsert_chat
from app.services.user import upsert_user


class DBMiddleware(BaseMiddleware):
    def __init__(self, pool: sessionmaker):
        self.pool = pool

    async def __call__(
            self,
            handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
            event: TelegramObject,
            data: Dict[str, Any]
    ) -> Any:
        async with self.pool() as session:
            holder_dao = HolderDao.create(session)
            data["dao"] = holder_dao
            data["user"] = await save_user(data, holder_dao)
            data["chat"] = await save_chat(data, holder_dao)
            await handler(event, data)
            del data["dao"]


async def save_user(data: Dict[str, Any], holder_dao: HolderDao):
    return await upsert_user(
        user_mapper.from_aiogram_to_dto(data["event_from_user"]),
        holder_dao.user
    )


async def save_chat(data: Dict[str, Any], holder_dao: HolderDao):
    return await upsert_chat(
        chat_mapper.from_aiogram_to_dto(data["event_chat"]),
        holder_dao.chat
    )
