# Telegram-бот портфолио на aiogram 3.
# Запуск: python bot.py (перед этим задайте переменную окружения BOT_TOKEN).

import asyncio
import logging
import os
import sys
from html import escape

from aiogram import Bot, Dispatcher, F
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
)

import config

# Диспетчер принимает обновления от Telegram и передаёт их нужным обработчикам
dp = Dispatcher()


# ---------- Клавиатуры ----------

def main_menu() -> InlineKeyboardMarkup:
    """Главное меню: три кнопки, каждая в своей строке."""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="О себе", callback_data="about")],
            [InlineKeyboardButton(text="Работы", callback_data="projects")],
            [InlineKeyboardButton(text="Контакты", callback_data="contacts")],
        ]
    )


def back_menu() -> InlineKeyboardMarkup:
    """Одна кнопка «Назад в меню»."""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Назад в меню", callback_data="menu")],
        ]
    )


# ---------- Тексты разделов (берутся из config.py) ----------
# escape() защищает от ошибок, если в тексте есть символы < > &

def about_text() -> str:
    return "<b>О себе</b>\n\n" + escape(config.ABOUT_TEXT)


def projects_text() -> str:
    lines = ["<b>Работы</b>\n"]
    for number, project in enumerate(config.PROJECTS, start=1):
        lines.append(
            f"{number}. <b>{escape(project['title'])}</b>\n"
            f"{escape(project['description'])}\n"
            f"🔗 {escape(project['link'])}\n"
        )
    return "\n".join(lines)


def contacts_text() -> str:
    return (
        "<b>Контакты</b>\n\n"
        f"Telegram: {escape(config.CONTACTS['telegram'])}\n"
        f"Email: {escape(config.CONTACTS['email'])}"
    )


# ---------- Обработчики ----------

@dp.message(CommandStart())
async def cmd_start(message: Message) -> None:
    """Команда /start: приветствие и главное меню."""
    await message.answer(escape(config.WELCOME_TEXT), reply_markup=main_menu())


@dp.callback_query(F.data == "about")
async def show_about(callback: CallbackQuery) -> None:
    """Кнопка «О себе»: меняем сообщение на текст о себе."""
    await callback.message.edit_text(about_text(), reply_markup=back_menu())
    await callback.answer()  # убирает «часики» на кнопке


@dp.callback_query(F.data == "projects")
async def show_projects(callback: CallbackQuery) -> None:
    """Кнопка «Работы»: список проектов."""
    await callback.message.edit_text(
        projects_text(),
        reply_markup=back_menu(),
        disable_web_page_preview=True,  # без больших превью ссылок
    )
    await callback.answer()


@dp.callback_query(F.data == "contacts")
async def show_contacts(callback: CallbackQuery) -> None:
    """Кнопка «Контакты»."""
    await callback.message.edit_text(contacts_text(), reply_markup=back_menu())
    await callback.answer()


@dp.callback_query(F.data == "menu")
async def back_to_menu(callback: CallbackQuery) -> None:
    """Кнопка «Назад в меню»: снова показываем главное меню."""
    await callback.message.edit_text(
        escape(config.WELCOME_TEXT), reply_markup=main_menu()
    )
    await callback.answer()


@dp.message()
async def any_other_message(message: Message) -> None:
    """Любое другое сообщение: подсказываем про /start."""
    await message.answer("Нажми /start, чтобы открыть меню")


# ---------- Запуск ----------

async def main() -> None:
    # Читаем токен из переменной окружения
    token = os.getenv("BOT_TOKEN")
    if not token:
        print("Ошибка: не задана переменная окружения BOT_TOKEN.")
        print("Задайте её и запустите бота снова (см. README.md).")
        sys.exit(1)

    # Создаём бота; все сообщения по умолчанию размечаются как HTML
    bot = Bot(token=token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))

    print("Бот запущен. Остановить: Ctrl+C")
    # Бот сам опрашивает Telegram о новых сообщениях
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Бот остановлен.")
