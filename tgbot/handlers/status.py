import asyncio

from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton

from tgbot.filters.admin import AdminFilter
from tgbot.keyboards.inline import main_kb, MainMenu, ServiceMenu, services_status_kb, service_detail_kb, BackMenu
from tgbot.services.checker import ServiceChecker, SERVICES_CONFIG

status_router = Router()
status_router.message.filter(AdminFilter())


@status_router.message(CommandStart())
async def admin_start(message: Message):
    await message.reply("Привет! Панель управления ботами.", reply_markup=main_kb())


@status_router.callback_query(MainMenu.filter(F.choice == "status"))
async def bots_check(callback: CallbackQuery):
    await callback.answer()

    # Show loading message
    await callback.message.edit_text("🔄 Проверяю статус сервисов...")

    service_checker = ServiceChecker(SERVICES_CONFIG)
    results = service_checker.check_all_services()

    # Create status message
    message = "🩹 <b>Статусы ботов:</b>\n\n"
    for result in results:
        service_name = result['service']
        if service_name in SERVICES_CONFIG:
            display_name = SERVICES_CONFIG[service_name]['display_name']

            if result.get('active'):
                status_emoji = "✅"
                status_text = "работает"
            elif result.get('error'):
                status_emoji = "⚠️"
                status_text = "ошибка"
            else:
                status_emoji = "❌"
                status_text = "остановлен"

            message += f"{status_emoji} <b>{display_name}</b> - {status_text}\n"

    message += "\n👇 Выберите сервис для управления:"

    await callback.message.edit_text(
        message,
        reply_markup=services_status_kb(results),
        parse_mode="HTML"
    )


@status_router.callback_query(ServiceMenu.filter(F.action == "view"))
async def service_detail(callback: CallbackQuery, callback_data: ServiceMenu):
    await callback.answer()

    service_name = callback_data.service_name

    # Show loading message
    await callback.message.edit_text("🔄 Загружаю детали сервиса...")

    # Get service status for specific service
    service_checker = ServiceChecker([service_name])
    results = service_checker.check_all_services()

    if results:
        result = results[0]
        message = service_checker.format_service_message(service_name, result)
        keyboard = service_detail_kb(service_name, result)

        await callback.message.edit_text(
            message,
            reply_markup=keyboard,
            parse_mode="HTML"
        )
    else:
        await callback.message.edit_text(
            "❌ Ошибка получения статуса сервиса",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[[
                InlineKeyboardButton(text="🔙 Назад", callback_data=MainMenu(choice="status").pack())
            ]])
        )


@status_router.callback_query(ServiceMenu.filter(F.action.in_(["start", "stop", "restart"])))
async def service_control(callback: CallbackQuery, callback_data: ServiceMenu):
    await callback.answer()

    service_name = callback_data.service_name
    action = callback_data.action

    # Action descriptions
    action_names = {
        "start": "запуск",
        "stop": "остановка",
        "restart": "перезапуск"
    }

    action_name = action_names.get(action, action)
    display_name = SERVICES_CONFIG.get(service_name, {}).get('display_name', service_name)

    # Show loading message
    await callback.message.edit_text(f"🔄 Выполняю {action_name} сервиса {display_name}...")

    # Execute command
    success, command_message = await checker.execute_service_command(service_name, action)

    if success:
        result_message = f"✅ {action_name.capitalize()} сервиса {display_name} выполнен успешно!"
    else:
        result_message = f"❌ Ошибка при выполнении {action_name} сервиса {display_name}:\n{command_message}"

    # Return to service detail view
    await asyncio.sleep(2)  # Give time for service to change state

    # Get updated service status
    service_checker = ServiceChecker([service_name])
    results = service_checker.check_all_services()

    if results:
        result = results[0]
        updated_message = checker.format_service_message(service_name, result)
        updated_message = f"{result_message}\n\n{updated_message}"
        keyboard = service_detail_kb(service_name, result)

        await callback.message.edit_text(
            updated_message,
            reply_markup=keyboard,
            parse_mode="HTML"
        )
    else:
        await callback.message.edit_text(
            result_message,
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[[
                InlineKeyboardButton(text="🔙 Назад", callback_data=MainMenu(choice="status").pack())
            ]])
        )


@status_router.callback_query(BackMenu.filter(F.to == "main"))
async def back_to_main(callback: CallbackQuery):
    await callback.answer()
    await callback.message.edit_text("Панель управления ботами.", reply_markup=main_kb())


