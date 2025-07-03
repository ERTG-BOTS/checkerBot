import asyncio
import concurrent.futures
import subprocess
from datetime import datetime
from typing import Dict, List

SERVICES_CONFIG = {
    'achievmentbot.service': {
        'name': '🏆 НТП Ачивер',
        'display_name': 'НТП Ачивер'
    },
    'nckachievenmentbot.service': {
        'name': '🏆 НЦК Ачивер',
        'display_name': 'НЦК Ачивер'
    },
    'stpquestion.service': {
        'name': '❓ НТП Вопросник',
        'display_name': 'НТП Вопросник'
    },
    'nckquestion.service': {
        'name': '❓ НЦК Вопросник',
        'display_name': 'НЦК Вопросник'
    },
    'ntposchedule.service': {
        'name': '🕞 НТП График',
        'display_name': 'НТП График'
    },
    'nckschedule.service': {
        'name': '🕞 НЦК График',
        'display_name': 'НЦК График'
    },
    'gifter.service': {
        'name': '🎁 Гифтер',
        'display_name': 'Гифтер'
    },
    'nckobsh.service': {
        'name': '👨‍👨 Общий ряд',
        'display_name': 'Общий ряд'
    },
    'nckteach.service': {
        'name': '🎓 NCKTeach',
        'display_name': 'NCKTeach'
    },
    'oliver.service': {
        'name': 'Оливер',
        'display_name': 'Оливер'
    },
    'addbot.service': {
        'name': '🥇 День достижений',
        'display_name': 'День достижений'
    },
}


class ServiceChecker:
    def __init__(self, services: List[str]):
        self.services = services

    def get_service_status(self, service_name: str) -> Dict:
        """Get the status of a single service and its last 5 log messages."""
        try:
            # Get service status
            status_result = subprocess.run(
                ['systemctl', 'is-active', service_name],
                capture_output=True,
                text=True,
                timeout=10
            )

            # Get detailed service info
            show_result = subprocess.run(
                ['systemctl', 'show', service_name, '--no-page'],
                capture_output=True,
                text=True,
                timeout=10
            )

            # Get last 5 log messages
            log_result = subprocess.run(
                ['journalctl', '-u', service_name, '-n', '5', '--no-pager', '--output=short'],
                capture_output=True,
                text=True,
                timeout=10
            )

            # Parse service info
            service_info = {}
            for line in show_result.stdout.strip().split('\n'):
                if '=' in line:
                    key, value = line.split('=', 1)
                    service_info[key] = value

            # Format log messages
            log_messages = []
            if log_result.stdout.strip():
                log_lines = log_result.stdout.strip().split('\n')
                for line in log_lines:
                    if line.strip():
                        log_messages.append(line)

            # Check for errors in logs
            has_error = any(
                'error' in log.lower() or 'failed' in log.lower() or 'exception' in log.lower()
                for log in log_messages
            )

            return {
                'service': service_name,
                'status': status_result.stdout.strip(),
                'active': status_result.stdout.strip() == 'active',
                'load_state': service_info.get('LoadState', 'unknown'),
                'sub_state': service_info.get('SubState', 'unknown'),
                'main_pid': service_info.get('MainPID', 'unknown'),
                'memory_usage': service_info.get('MemoryCurrent', 'unknown'),
                'cpu_usage': service_info.get('CPUUsageNSec', 'unknown'),
                'last_logs': log_messages,
                'has_log_errors': has_error,
                'error': None,
                'checked_at': datetime.now().isoformat()
            }

        except subprocess.TimeoutExpired:
            return {
                'service': service_name,
                'status': 'timeout',
                'active': False,
                'error': 'Command timed out',
                'checked_at': datetime.now().isoformat()
            }
        except Exception as e:
            return {
                'service': service_name,
                'status': 'error',
                'active': False,
                'error': str(e),
                'checked_at': datetime.now().isoformat()
            }

    def check_all_services(self) -> List[Dict]:
        """Check all services in parallel."""
        results = []

        with concurrent.futures.ThreadPoolExecutor(max_workers=len(self.services)) as executor:
            # Submit all tasks
            future_to_service = {
                executor.submit(self.get_service_status, service): service
                for service in self.services
            }

            # Collect results
            for future in concurrent.futures.as_completed(future_to_service):
                try:
                    result = future.result()
                    results.append(result)
                except Exception as e:
                    service = future_to_service[future]
                    results.append({
                        'service': service,
                        'status': 'error',
                        'active': False,
                        'error': f'Future execution failed: {str(e)}',
                        'checked_at': datetime.now().isoformat()
                    })

        return results

    def format_service_message(self, service_name, result):
        """Format service status message"""
        display_name = SERVICES_CONFIG.get(service_name, {}).get('display_name', service_name)

        # Status emoji and text
        if result.get('active'):
            status_emoji = "✅"
            status_text = "работает"
        elif result.get('error'):
            status_emoji = "⚠️"
            status_text = "ошибка"
        else:
            status_emoji = "❌"
            status_text = "остановлен"

        message = f"🤖 <b>{display_name}</b>\n"
        message += f"Статус: {status_emoji} {status_text}\n\n"

        # Add service details if available
        if not result.get('error'):
            if result.get('main_pid') != 'unknown':
                message += f"PID: {result.get('main_pid')}\n"
            if result.get('sub_state') != 'unknown':
                message += f"Состояние: {result.get('sub_state')}\n"
            message += "\n"

        # Add last 5 log messages
        logs = result.get('last_logs', [])
        if logs:
            message += f"📝 <b>Последние {len(logs)} записей лога:</b>\n"
            for i, log in enumerate(logs, 1):
                # Truncate long log messages
                if len(log) > 100:
                    log = log[:97] + "..."
                message += f"{i}. <code>{log}</code>\n"
        else:
            message += "📝 <b>Логи не найдены</b>\n"

        if result.get('error'):
            message += f"\n❌ <b>Ошибка:</b> {result['error']}"

        return message

    async def execute_service_command(self, service_name, action):
        """Execute systemctl command asynchronously"""
        try:
            if action == "start":
                cmd = ["sudo", "systemctl", "start", service_name]
            elif action == "stop":
                cmd = ["sudo", "systemctl", "stop", service_name]
            elif action == "restart":
                cmd = ["sudo", "systemctl", "restart", service_name]
            else:
                return False, "Неизвестная команда"

            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )

            stdout, stderr = await process.communicate()

            if process.returncode == 0:
                return True, "Команда выполнена успешно"
            else:
                return False, f"Ошибка: {stderr.decode()}"

        except Exception as e:
            return False, f"Ошибка выполнения: {str(e)}"


services = list(SERVICES_CONFIG.keys())
checker = ServiceChecker(services)