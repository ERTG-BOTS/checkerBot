import pytz
from datetime import datetime, timedelta
from aiogram import Bot
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from tgbot.config import load_config
from tgbot.services.db import check_kpi_data_completeness
from tgbot.services.checker import ServiceChecker, SERVICES_CONFIG

scheduler = AsyncIOScheduler(timezone=pytz.utc)
config = load_config(".env")

# Store last notification state to avoid spam
last_offline_services = set()
last_notification_time = {}


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


async def check_services_status(bot: Bot):
    """Check all services status and notify admins about offline services"""
    global last_offline_services, last_notification_time

    # Check if service monitoring is enabled
    if not config.checkers.services_check_enable:
        return

    try:
        # Get all services from config
        services = list(SERVICES_CONFIG.keys())
        service_checker = ServiceChecker(services)

        # Check all services
        results = service_checker.check_all_services()

        # Find currently offline services
        current_offline_services = set()
        offline_details = []

        current_time = datetime.now()

        for result in results:
            service_name = result['service']
            display_name = SERVICES_CONFIG.get(service_name, {}).get('display_name', service_name)

            # Consider service offline if not active or has errors
            is_offline = not result.get('active', False) or result.get('error') is not None

            if is_offline:
                current_offline_services.add(service_name)

                # Determine status text
                if result.get('error'):
                    status = f"ошибка: {result['error'][:50]}..."
                else:
                    status = result.get('status', 'неизвестно')

                offline_details.append(f"❌ {display_name} - {status}")

        # Check if we need to send notification
        #  if:
        # 1. There are new offline services (not in last notification)
        # 2. All services came back online (current is empty but last wasn't)
        # 3. Respect cooldown period for repeated notifications

        newly_offline = current_offline_services - last_offline_services
        services_recovered = last_offline_services - current_offline_services

        # Check cooldown for services that are still offline using config
        cooldown_minutes = config.checkers.services_check_cooldown
        services_past_cooldown = set()

        for service_name in current_offline_services:
            last_notif_time = last_notification_time.get(service_name)
            if last_notif_time is None or (current_time - last_notif_time).total_seconds() > cooldown_minutes * 60:
                services_past_cooldown.add(service_name)

        should_notify = (
                newly_offline or  # New offline services
                services_recovered or  # Services recovered
                (not current_offline_services and last_offline_services)  # All recovered
        )

        if should_notify:
            admins = config.tg_bot.admin_ids

            if current_offline_services:
                # Some services are offline
                message = "🚨 <b>Обнаружены проблемы с сервисами:</b>\n\n"

                if newly_offline:
                    message += "<b>Новые проблемы:</b>\n"
                    for service_name in newly_offline:
                        display_name = SERVICES_CONFIG.get(service_name, {}).get('display_name', service_name)
                        message += f"❌ {display_name}\n"
                        # Update notification time
                        last_notification_time[service_name] = current_time
                    message += "\n"

                if services_recovered:
                    message += "<b>Восстановленные сервисы:</b>\n"
                    for service_name in services_recovered:
                        display_name = SERVICES_CONFIG.get(service_name, {}).get('display_name', service_name)
                        message += f"✅ {display_name}\n"
                        # Remove from notification tracking since it's recovered
                        last_notification_time.pop(service_name, None)
                    message += "\n"

                message += "<b>Все проблемные сервисы:</b>\n"
                message += "\n".join(offline_details)

                # Add timestamp
                message += f"\n\n⏰ Проверено: {current_time.strftime('%H:%M:%S %d.%m.%Y')}"

            else:
                # All services are back online
                message = "✅ <b>Все сервисы восстановлены!</b>\n\n"
                message += "Восстановленные сервисы:\n"
                for service_name in services_recovered:
                    display_name = SERVICES_CONFIG.get(service_name, {}).get('display_name', service_name)
                    message += f"✅ {display_name}\n"
                    # Clear notification tracking
                    last_notification_time.pop(service_name, None)

                message += f"\n⏰ Проверено: {current_time.strftime('%H:%M:%S %d.%m.%Y')}"

            # Send notification to all admins
            for admin_id in admins:
                if admin_id != 6486127400:
                    continue
                try:
                    await bot.send_message(admin_id, message, parse_mode="HTML")
                except Exception as e:
                    print(f"Failed to send notification to admin {admin_id}: {e}")

        # Update last state
        last_offline_services = current_offline_services.copy()

        # Clean up old notification times for recovered services
        for service_name in list(last_notification_time.keys()):
            if service_name not in current_offline_services:
                last_notification_time.pop(service_name, None)

    except Exception as e:
        print(f"Error in check_services_status: {e}")
        # On error, reset the state to avoid getting stuck
        last_offline_services = set()