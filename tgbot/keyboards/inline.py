from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from tgbot.misc.checker import SERVICES_CONFIG


class MainMenu(CallbackData, prefix='main'):
    choice: str


class ServiceMenu(CallbackData, prefix='service'):
    service_name: str
    action: str  # 'view', 'start', 'stop', 'restart'


class ProceduresMenu(CallbackData, prefix='procedure'):
    procedure: str


class BackMenu(CallbackData, prefix='back'):
    to: str


def main_kb():
    buttons = [
        [
            InlineKeyboardButton(text="🩹 Статусы ботов",
                                 callback_data=MainMenu(choice="status").pack()),
        ], [
            InlineKeyboardButton(text="📊 Показатели",
                                 callback_data=MainMenu(choice="kpi").pack()),
        ],
    ]

    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard


def services_status_kb(results):
    """Create keyboard with service statuses"""
    builder = InlineKeyboardBuilder()

    for result in results:
        service_name = result['service']
        if service_name in SERVICES_CONFIG:
            # Determine status emoji
            if result.get('active'):
                status_emoji = "✅"
            elif result.get('error'):
                status_emoji = "⚠️"
            else:
                status_emoji = "❌"

            display_name = SERVICES_CONFIG[service_name]['display_name']
            button_text = f"{status_emoji} {display_name}"

            builder.button(
                text=button_text,
                callback_data=ServiceMenu(service_name=service_name, action="view").pack()
            )

    # Add back button
    builder.button(text="🔙 Назад", callback_data=BackMenu(to="main").pack())
    builder.adjust(2)  # One button per row

    return builder.as_markup()


def service_detail_kb(service_name, service_status):
    """Create keyboard for individual service management"""
    builder = InlineKeyboardBuilder()

    is_active = service_status.get('active', False)
    has_error = service_status.get('error') is not None

    if is_active:
        # Service is running - show restart and stop
        builder.button(
            text="🔄 Перезапуск",
            callback_data=ServiceMenu(service_name=service_name, action="restart").pack()
        )
        builder.button(
            text="⏹️ Остановить",
            callback_data=ServiceMenu(service_name=service_name, action="stop").pack()
        )
    elif has_error:
        # Service has error - show restart and stop
        builder.button(
            text="🔄 Перезапуск",
            callback_data=ServiceMenu(service_name=service_name, action="restart").pack()
        )
        builder.button(
            text="⏹️ Остановить",
            callback_data=ServiceMenu(service_name=service_name, action="stop").pack()
        )
    else:
        # Service is stopped - show start
        builder.button(
            text="▶️ Запустить",
            callback_data=ServiceMenu(service_name=service_name, action="start").pack()
        )

    # Add back button
    builder.button(text="🔙 К списку", callback_data=MainMenu(choice="status").pack())
    builder.adjust(2, 1)  # Two buttons in first row, one in second

    return builder.as_markup()


def procedures_kb():
    buttons = [
        [
            InlineKeyboardButton(text="☀️ День",
                                 callback_data=ProceduresMenu(procedure="day").pack()),
            InlineKeyboardButton(text="☀️ Неделя",
                                 callback_data=ProceduresMenu(procedure="week").pack())
        ], [
            InlineKeyboardButton(text="🗓️ Месяц",
                                 callback_data=ProceduresMenu(procedure="month").pack()),
        ],
        [
            InlineKeyboardButton(text="🔙 Назад", callback_data=BackMenu(to="main").pack()),
        ],
    ]

    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard
