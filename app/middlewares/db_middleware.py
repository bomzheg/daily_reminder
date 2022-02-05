from typing import Callable, Any, Awaitable

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject
from sqlalchemy.orm import sessionmaker

from app.dao.holder import HolderDao
from app.models import dto
from app.services.chat import upsert_chat
from app.services.user import upsert_user


class DBMiddleware(BaseMiddleware):
    def __init__(self, pool: sessionmaker):
        self.pool = pool

    async def __call__(
            self,
            handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
            event: TelegramObject,
            data: dict[str, Any]
    ) -> Any:
        async with self.pool() as session:
            holder_dao = HolderDao.create(session)
            data["dao"] = holder_dao
            data["user"] = await save_user(data, holder_dao)
            data["chat"] = await save_chat(data, holder_dao)
            result = await handler(event, data)
            del data["dao"]
            return result


async def save_user(data: dict[str, Any], holder_dao: HolderDao) -> dto.User:
    return await upsert_user(
        dto.User.from_aiogram(data["event_from_user"]),
        holder_dao.user
    )


async def save_chat(data: dict[str, Any], holder_dao: HolderDao) -> dto.Chat:
    return await upsert_chat(
        dto.Chat.from_aiogram(data["event_chat"]),
        holder_dao.chat
    )
