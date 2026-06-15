from aiogram import Router
from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
    CallbackQuery
)
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram import F

menu_router = Router()


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


@menu_router.message(F.text == "🍕 Смотреть меню")
async def menu(message: Message, db):

    user = await db.get_user(message.from_user.id)
    if user:
        pass
    else:
        await db.add_user(message.from_user.id, message.from_user.username, message.from_user.first_name)

    await message.answer(
        "Выбери интересующую категорию из меню ниже: 👇",
        reply_markup=await get_inline_category()
    )


@menu_router.callback_query(F.data.in_({"pizza", "snacks", "drinks", "desserts"}))
async def menu(callback: CallbackQuery, db):
    category = callback.data

    products = await db.get_products_by_category(category)

    if not products:
        await callback.message.answer("📭 В этой категории пока нет товаров...")
        return

    builder = InlineKeyboardBuilder()

    for item in products:
        button_text = f"{item['title']} — {item['price']:.2f} BYN"
        callback_data = f"prod_{item['product_id']}"
        builder.button(text=button_text, callback_data=callback_data)

    builder.button(text="⬅️ Назад в категории", callback_data="back_to_categories")

    builder.adjust(1)

    await callback.message.edit_text(
        text=f"Выбери товар из категории {category.capitalize()}: 👇",
        reply_markup=builder.as_markup()
    )
    await callback.answer()


@menu_router.callback_query(F.data.startswith("prod_"))
async def show_product(callback: CallbackQuery, db):
    product_id = int(callback.data.split("_")[1])
    item = await db.get_products(product_id=product_id)

    title = item['title']
    price = item['price']
    description = item['description']
    image_url = item['image_url']
    category = item['category']

    text = (
        f"<a href='{image_url}'>&#8203;</a>"
        f"🍕 <b>{title}</b>\n\n"
        f"📋 <b>Описание:</b>\n{description or 'Описание временно отсутствует.'}\n\n"
        f"💰 <b>Цена:</b> {price:.2f} BYN"
    )

    builder = InlineKeyboardBuilder()

    builder.button(text="🛒 Добавить в корзину", callback_data=f"buy_{product_id}")
    builder.button(text="⬅️ Назад к списку", callback_data=category)

    builder.adjust(2)

    await callback.message.edit_text(
        text=text,
        reply_markup=builder.as_markup(),
        parse_mode="HTML"
    )
    await callback.answer()


@menu_router.callback_query(F.data == "back_to_categories")
async def back_to_categories(callback: CallbackQuery):
    await callback.message.edit_text(
        text="Выбери интересующую категорию из меню ниже: 👇",
        reply_markup=await get_inline_category()
    )
    await callback.answer()
