from aiogram.filters import Command
from aiogram import Router, F
from aiogram.types import (
    ReplyKeyboardMarkup,
    KeyboardButton,
    Message,
)

main_router = Router()


async def get_main_reply_keyboard():
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text='🍕 Смотреть меню'), KeyboardButton(text='🧺 Корзина')
            ],
            [
                KeyboardButton(text='👤 Профиль')
            ]
        ],
        resize_keyboard=True
    )
    return keyboard


@main_router.message(Command('start'))
async def start(message: Message, db):
    user = await db.get_user(message.from_user.id)
    if user:
        await message.answer("С возвращением!")
    else:
        await message.answer("Привет! Я тебя зарегистрировал.")
        await db.add_user(message.from_user.id, message.from_user.username, message.from_user.first_name)

    welcome_text = (
        f"Привет, {message.from_user.first_name}! 👋\n"
        f"Добро пожаловать в **PizzaFox** — твой быстрый гид по самой вкусной пицце! 🦊🍕\n\n"
        f"Я помогу тебе выбрать и заказать горячую пиццу, закуски и напитки прямо здесь, не выходя из Telegram.\n\n"
        f"👇 Используй меню ниже, чтобы заглянуть в корзину, посмотреть профиль или сделать свой первый заказ!"
    )
    await message.answer(welcome_text, parse_mode="Markdown", reply_markup=await get_main_reply_keyboard())


@main_router.message(F.text == "👤 Профиль")
async def show_profile(message: Message, db):

    user = await db.get_user(message.from_user.id)
    if user:
        pass
    else:
        await db.add_user(message.from_user.id, message.from_user.username, message.from_user.first_name)

    name = user['first_name'] or "Гость"
    total_orders = user['total_orders'] or 0
    total_spent = user['total_spent'] or 0.0

    profile_text = (
        f"👤 <b>Ваш профиль:</b>\n\n"
        f"Имя: {name}\n"
        f"Количество заказов: {total_orders}\n"
        f"Потрачено: {total_spent:.2f} BYN"
    )
    await message.answer(profile_text, parse_mode="HTML")