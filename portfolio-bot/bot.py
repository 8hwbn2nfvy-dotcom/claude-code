# Telegram-бот портфолио на aiogram 3.
# Запуск: python bot.py (перед этим задайте переменную окружения BOT_TOKEN).

import asyncio
import logging
import os
import sys
from datetime import datetime
from html import escape

from aiogram import Bot, Dispatcher, F
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    LinkPreviewOptions,
    Message,
)

import config

# Диспетчер принимает обновления от Telegram и передаёт их нужным обработчикам
dp = Dispatcher()

# ID администратора в Telegram: ему бот пересылает заявки (необязательно)
ADMIN_ID = os.getenv("ADMIN_ID")

# Файл, куда сохраняются все заявки
ORDERS_FILE = "orders.txt"


# ---------- Шаги заявки ----------

class Order(StatesGroup):
    """Бот запоминает, на каком шаге заявки находится пользователь."""
    name = State()     # ждём имя
    task = State()     # ждём описание проекта
    contact = State()  # ждём контакт


# ---------- Клавиатуры ----------

def main_menu() -> InlineKeyboardMarkup:
    """Главное меню: каждая кнопка в своей строке."""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="О себе", callback_data="about")],
            [InlineKeyboardButton(text="Работы", callback_data="projects")],
            [InlineKeyboardButton(text="Контакты", callback_data="contacts")],
            [InlineKeyboardButton(text="Заказать проект", callback_data="order")],
        ]
    )


def back_menu() -> InlineKeyboardMarkup:
    """Одна кнопка «Назад в меню»."""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Назад в меню", callback_data="menu")],
        ]
    )


def cancel_menu() -> InlineKeyboardMarkup:
    """Кнопка отмены заявки."""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Отмена", callback_data="cancel")],
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


# ---------- Меню и разделы ----------

@dp.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext) -> None:
    """Команда /start: приветствие и главное меню."""
    await state.clear()  # если человек был посреди заявки — сбрасываем её
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
        link_preview_options=LinkPreviewOptions(is_disabled=True),  # без превью ссылок
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


# ---------- Заявка «Заказать проект» ----------

@dp.callback_query(F.data == "order")
async def order_start(callback: CallbackQuery, state: FSMContext) -> None:
    """Начало заявки: спрашиваем имя."""
    await state.set_state(Order.name)
    await callback.message.answer(config.ORDER_ASK_NAME, reply_markup=cancel_menu())
    await callback.answer()


@dp.callback_query(F.data == "cancel")
async def order_cancel(callback: CallbackQuery, state: FSMContext) -> None:
    """Кнопка «Отмена»: сбрасываем заявку и показываем меню."""
    await state.clear()
    await callback.message.edit_text("Заявка отменена.")
    await callback.message.answer(escape(config.WELCOME_TEXT), reply_markup=main_menu())
    await callback.answer()


@dp.message(Command("cancel"))
async def cmd_cancel(message: Message, state: FSMContext) -> None:
    """Команда /cancel делает то же, что кнопка «Отмена»."""
    await state.clear()
    await message.answer("Заявка отменена.", reply_markup=main_menu())


@dp.message(Order.name, F.text)
async def order_name(message: Message, state: FSMContext) -> None:
    """Получили имя — спрашиваем, какой нужен проект."""
    await state.update_data(name=message.text)
    await state.set_state(Order.task)
    await message.answer(config.ORDER_ASK_TASK, reply_markup=cancel_menu())


@dp.message(Order.task, F.text)
async def order_task(message: Message, state: FSMContext) -> None:
    """Получили описание — спрашиваем контакт."""
    await state.update_data(task=message.text)
    await state.set_state(Order.contact)
    await message.answer(config.ORDER_ASK_CONTACT, reply_markup=cancel_menu())


@dp.message(Order.contact, F.text)
async def order_contact(message: Message, state: FSMContext, bot: Bot) -> None:
    """Получили контакт — сохраняем заявку и отправляем админу."""
    data = await state.get_data()
    await state.clear()

    user = message.from_user
    username = f"@{user.username}" if user.username else "нет ника"
    order_text = (
        f"Дата: {datetime.now():%Y-%m-%d %H:%M}\n"
        f"Пользователь: {user.full_name} ({username}, id {user.id})\n"
        f"Имя: {data['name']}\n"
        f"Проект: {data['task']}\n"
        f"Контакт: {message.text}\n"
    )

    # 1) Сохраняем заявку в файл
    with open(ORDERS_FILE, "a", encoding="utf-8") as file:
        file.write(order_text + "-" * 30 + "\n")

    # 2) Отправляем заявку администратору, если задан ADMIN_ID
    if ADMIN_ID:
        try:
            await bot.send_message(
                ADMIN_ID, "<b>Новая заявка</b>\n\n" + escape(order_text)
            )
        except Exception as error:
            logging.error("Не удалось отправить заявку админу: %s", error)

    await message.answer(config.ORDER_DONE_TEXT, reply_markup=main_menu())


@dp.message(Order.name)
@dp.message(Order.task)
@dp.message(Order.contact)
async def order_not_text(message: Message) -> None:
    """Во время заявки прислали не текст (фото, стикер и т.п.)."""
    await message.answer("Пожалуйста, напиши ответ текстом или нажми «Отмена».")


# ---------- Всё остальное ----------

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

    if not ADMIN_ID:
        print("ADMIN_ID не задан: заявки будут только сохраняться в orders.txt.")

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
