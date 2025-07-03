from aiogram.filters import BaseFilter
from aiogram.types import Message

from tgbot.config import Config
from tgbot.misc.db import is_admin


class AdminFilter(BaseFilter):
    is_admin: bool = True

    async def __call__(self, obj: Message, config: Config) -> bool:
        return (is_admin(obj.from_user.id)) == self.is_admin
