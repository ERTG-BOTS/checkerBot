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
6. Запусти `bot.py` через venv или запусти `bot-checker.service` как сервис

## С докером (пока не готово)
1. `git clone https://github.com/ERTG-BOTS/bot-checker.git`
2. `cd bot-checker`
3. `docker compose up -d`

