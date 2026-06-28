from aiogram.types import (
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)


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


async def get_inline_category():
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🍕 Пицца", callback_data="pizza")],
            [InlineKeyboardButton(text="🍿 Закуски", callback_data="snacks")],
            [InlineKeyboardButton(text="🥤 Напитки", callback_data="drinks")],
            [InlineKeyboardButton(text="🍰 Десерты", callback_data="desserts")],
        ]
    )
    return keyboard
