# Ссылки
https://t.me/botboots_bot

# Системные требования
```bash
apt install unixodbc msodbcsql17
```

# Установка
## Без докера
1. `git clone https://github.com/ERTG-BOTS/bot-checker.git`
2. `cd bot-checker`
3. `python -m venv venv`
4. `source venv/bin/activate`
5. `pip install -r requirements.txt`
6. Запусти `bot.py` через venv или `bot-checker.service` как сервис

## С докером (пока не готово)
1. `git clone https://github.com/ERTG-BOTS/bot-checker.git`
2. `cd bot-checker`
3. `docker compose up -d`

# Проверки
## Статусы ботов
На текущий момент проверяется статус следующих сервисов на машине, где запущен бот:
- `adaptive.service`
- `achievmentbot.service`
- `nckachievenmentbot.service`
- `stpquestion.service`
- `nckquestion.service`
- `ntposchedule.service`
- `nckschedule.service`
- `gifter.service`
- `nckobsh.service`
- `nckteach.service`

Уведомление об изменении состояния сервиса отправляется администраторам, указанным в .env в переменной ADMINS

## Обновление KPI
На текущий момент проверяется наличие обновлений в таблице KPIRAW в базе STPMain. Сравниваются даты, указанные в столбце DATA с реальной текущей датой. В случае несовпадения дат отправляется уведомление администраторам, указанным в .env в переменной ADMINS

Уведомление об изменении состояния сервиса отправляется администраторам, указанным в .env в переменной ADMINS

# Переменные
```
BOT_TOKEN(str): Токен бота из @botfather
ADMINS (list[int]): Список ID чатов админов

DB_HOST (str): Адрес сервера базы данных
DB_USER (str): Имя пользователя базы данных
DB_PASSWORD (str): Пароль пользователя базы данных
DB_NAME (str): Название базы данных

KPI_CHECK_ENABLE (bool): Статус активности проверки KPI
KPI_CHECK_HOUR (int): Время запуска проверки KPI

SERVICES_CHECK_ENABLE (bool): Статус активности проверки статуса сервисов
SERVICES_CHECK_INTERVAL (int): Время запуска проверки статуса сервисов
SERVICES_CHECK_COOLDOWN (int): Время игнорирования лежащего сервиса после предыдущего уведомления```
