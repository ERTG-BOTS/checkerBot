from aiogram import Router, F
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton

from tgbot.filters.admin import AdminFilter
from tgbot.keyboards.inline import MainMenu, procedures_kb, ProceduresMenu, procedures_confirm_kb, ProceduresConfirmMenu
from tgbot.services.db import run_procedure

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
async def procedure_confirm(callback: CallbackQuery, callback_data: ProceduresMenu):
    await callback.answer()

    picked_variant = callback_data.procedure

    # Map procedure codes to display names
    procedure_names = {
        "day": "обновление статистики за день",
        "week": "обновление статистики за неделю",
        "month": "обновление статистики за месяц"
    }

    procedure_name = procedure_names.get(picked_variant, "неизвестную процедуру")

    await callback.message.edit_text(
        f"⚠️ <b>Подтверждение действия</b>\n\n"
        f"Ты уверен, что хочешь запустить процедуру:\n"
        f"<i>{procedure_name}</i>?\n\n"
        f"Процедура может занять некоторое время.",
        reply_markup=procedures_confirm_kb(picked_variant),
        parse_mode="HTML"
    )


@kpi_router.callback_query(ProceduresConfirmMenu.filter(F.action == "confirm"))
async def procedure_execute(callback: CallbackQuery, callback_data: ProceduresConfirmMenu):
    await callback.answer()

    picked_variant = callback_data.procedure

    # Show loading message
    await callback.message.edit_text(
        "⏳ <b>Выполняется процедура...</b>\n\n"
        "Пожалуйста, подожди. Это может занять несколько минут."
    )

    try:
        success, message = None, None

        match picked_variant:
            case "day":
                success, message = await run_procedure("UpdateKPIStatsDay")
            case "week":
                success, message = await run_procedure("UpdateKPIStatsWeek")
            case "month":
                success, message = await run_procedure("UpdateKPIStatsMonth")
            case _:
                success, message = False, "Неизвестная процедура"

        if success:
            result_text = (
                "✅ <b>Процедура выполнена успешно!</b>\n\n"
                f"Результат: {message if message else 'Операция завершена'}"
            )
        else:
            result_text = (
                "❌ <b>Ошибка выполнения процедуры</b>\n\n"
                f"Детали: {message if message else 'Неизвестная ошибка'}"
            )

    except Exception as e:
        result_text = (
            "❌ <b>Критическая ошибка</b>\n\n"
            f"Не удалось выполнить процедуру: {str(e)}"
        )

    # Return to main KPI menu
    back_button = InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text="🔙 К выбору процедур",
                             callback_data=MainMenu(choice="kpi").pack())
    ]])

    await callback.message.edit_text(
        result_text,
        reply_markup=back_button,
        parse_mode="HTML"
    )


@kpi_router.callback_query(ProceduresConfirmMenu.filter(F.action == "cancel"))
async def procedure_cancel(callback: CallbackQuery):
    await callback.answer()
    await callback.message.edit_text(
        "📊 Выбери процедуру для запуска",
        reply_markup=procedures_kb()
    )