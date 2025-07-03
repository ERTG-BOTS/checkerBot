import asyncio

from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.filters.callback_data import CallbackData
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton

from tgbot.filters.admin import AdminFilter
from tgbot.keyboards.inline import main_kb, MainMenu, ServiceMenu, services_status_kb, service_detail_kb, BackMenu, \
    procedures_kb, ProceduresMenu
from tgbot.misc.checker import ServiceChecker, SERVICES_CONFIG, checker
from tgbot.misc.db import run_procedure

kpi_router = Router()
kpi_router.message.filter(AdminFilter())


@kpi_router.callback_query(MainMenu.filter(F.choice == "kpi"))
async def kpi_check(callback: CallbackQuery):
    await callback.answer()
    await callback.message.edit_text(
        "📊 Выбери процедуру для запуска",
        reply_markup=procedures_kb()
    )


@kpi_router.callback_query(ProceduresMenu.filter())
async def procedure(callback: CallbackQuery, callback_data: ProceduresMenu):
    picked_variant = callback_data.procedure

    match picked_variant:
        case "day":
            await run_procedure("UpdateKPIStatsDay")
        case "week":
            await run_procedure("UpdateKPIStatsWeek")
        case "month":
            await run_procedure("UpdateKPIStatsMonth")

    await callback.answer("Процедура запущена!")
