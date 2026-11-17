# Бот-портфолио для Telegram

Простой бот на Python и aiogram 3. Показывает меню «О себе», «Работы», «Контакты»
и принимает заявки через кнопку «Заказать проект».

## Файлы

- `bot.py` — запуск бота и обработчики кнопок и команд.
- `config.py` — все тексты: о себе, проекты, контакты. Меняйте только его.
- `requirements.txt` — зависимости.

## 1. Установка

Нужен Python 3.9 или новее.

```bash
python -m venv venv
# Linux / macOS:
source venv/bin/activate
# Windows:
venv\Scripts\activate

pip install -r requirements.txt
```

## 2. Токен и ID администратора

Получите токен у [@BotFather](https://t.me/BotFather) (команда `/newbot`) и задайте переменную окружения `BOT_TOKEN`:

```bash
# Linux / macOS
export BOT_TOKEN="ваш_токен"

# Windows (PowerShell)
$env:BOT_TOKEN="ваш_токен"

# Windows (cmd)
set BOT_TOKEN=ваш_токен
```

Не публикуйте токен и не добавляйте его в код.

Чтобы получать заявки в Telegram, задайте ещё `ADMIN_ID` — ваш числовой ID
(его можно узнать у бота [@userinfobot](https://t.me/userinfobot)):

```bash
export ADMIN_ID="123456789"
```

Без `ADMIN_ID` бот тоже работает: заявки просто сохраняются в файл `orders.txt`.
Чтобы бот смог написать вам, сначала сами отправьте ему `/start`.

## 3. Запуск

```bash
python bot.py
```

Откройте бота в Telegram и отправьте `/start`. Остановить бота — `Ctrl+C`.

## Заявки «Заказать проект»

Бот по очереди спрашивает имя, описание проекта и контакт. Готовая заявка:
- дописывается в файл `orders.txt` (рядом с `bot.py`);
- приходит вам в Telegram, если задан `ADMIN_ID`.

Отменить заявку — кнопка «Отмена» или команда `/cancel`. Тексты вопросов меняются в `config.py`.

## Запуск на сервере (Linux, systemd)

Так бот работает круглосуточно и сам перезапускается после сбоя или перезагрузки сервера.
Пример для Ubuntu/Debian и пользователя `ubuntu` — подставьте своего.

1. Скопируйте проект на сервер и установите зависимости:

   ```bash
   sudo apt update && sudo apt install -y git python3 python3-venv
   git clone -b claude/affectionate-fermat-epr3o9 https://github.com/8hwbn2nfvy-dotcom/claude-code.git
   cd claude-code/portfolio-bot
   python3 -m venv venv
   venv/bin/pip install -r requirements.txt
   ```

   Если репозиторий приватный, `git clone` попросит вход в GitHub —
   или просто скопируйте папку `portfolio-bot` на сервер через `scp`.

2. Сохраните токен в файл `.env` (он в `.gitignore` и не попадёт в репозиторий):

   ```bash
   printf 'BOT_TOKEN=ваш_токен\nADMIN_ID=123456789\n' > .env
   chmod 600 .env
   ```

3. Создайте службу `sudo nano /etc/systemd/system/portfolio-bot.service`:

   ```ini
   [Unit]
   Description=Telegram portfolio bot
   After=network-online.target

   [Service]
   User=ubuntu
   WorkingDirectory=/home/ubuntu/claude-code/portfolio-bot
   EnvironmentFile=/home/ubuntu/claude-code/portfolio-bot/.env
   ExecStart=/home/ubuntu/claude-code/portfolio-bot/venv/bin/python bot.py
   Restart=always
   RestartSec=5

   [Install]
   WantedBy=multi-user.target
   ```

4. Включите и запустите:

   ```bash
   sudo systemctl daemon-reload
   sudo systemctl enable --now portfolio-bot
   ```

Полезные команды:

```bash
sudo systemctl status portfolio-bot     # работает ли бот
journalctl -u portfolio-bot -f          # логи в реальном времени
sudo systemctl restart portfolio-bot    # перезапуск после изменения config.py
```

Обновить бота: `git pull` в папке проекта, затем `sudo systemctl restart portfolio-bot`.
Одновременно должен работать только один экземпляр бота с этим токеном —
остановите локальный запуск, если бот запущен на сервере.
