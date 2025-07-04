# System requirements
```bash
apt install unixodbc msodbcsql17
```

# Installation
## Without docker
1. `git clone https://github.com/ERTG-BOTS/bot-checker.git`
2. `cd bot-checker`
3. `python -m venv venv`
4. `source venv/bin/activate`
5. `pip install -r requirements.txt`
6. Run `bot.py` with venv or run `bot-checker.service` as systemd service

## With docker (not ready yet)
1. `git clone https://github.com/ERTG-BOTS/bot-checker.git`
2. `cd bot-checker`
3. `docker compose up -d`