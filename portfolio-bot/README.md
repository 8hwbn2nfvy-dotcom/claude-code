# Бот-портфолио для Telegram

Простой бот на Python и aiogram 3. Показывает меню «О себе», «Работы», «Контакты».

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

## 2. Токен

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

## 3. Запуск

```bash
python bot.py
```

Откройте бота в Telegram и отправьте `/start`. Остановить бота — `Ctrl+C`.
