import pytz
from aiogram import Bot
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from tgbot.config import load_config
from tgbot.services.db import check_kpi_data_completeness

scheduler = AsyncIOScheduler(timezone=pytz.utc)
config = load_config(".env")


async def kpi_check(bot: Bot):
    """Check KPI from DB"""
    kpi_completeness, wrong_divisions = await check_kpi_data_completeness()
    if kpi_completeness:
        return

    admins = config.tg_bot.admin_ids
    message = "⚠️ Обнаружено несоответствие в датах KPI для следующих отделов:\n"
    for division in wrong_divisions:
        message += f"- {division}\n"

    for admin in admins:
        await bot.send_message(admin, message)


async def check_status():
    pass
