import asyncio
import os.path

from aiogram.types import CallbackQuery, Message, FSInputFile
from aiogram import F, Router, Bot
from aiogram.utils.keyboard import InlineKeyboardBuilder
from handlers.pdf_creator import generate_pdf
from config import config

cart_router = Router()


@cart_router.callback_query(F.data == "open_cart")
async def show_cart_callback(callback: CallbackQuery, db):
    items = await db.get_items_in_cart(callback.from_user.id)
    if not items:
        await callback.message.answer("🛒 Корзина пуста")
        return

    builder = InlineKeyboardBuilder()
    text = "🛒 <b>Ваша корзина:</b>\n\n"

    for item in items:
        builder.button(text=f"❌ {item['title']} - {item['quantity']}", callback_data=f"edit_{item['product_id']}")

    builder.button(text="✅ Оформить", callback_data="checkout")
    builder.adjust(1)

    await callback.message.edit_text(text=text, reply_markup=builder.as_markup(), parse_mode="HTML")


@cart_router.message(F.text == "🧺 Корзина")
async def show_cart(message: Message, db):
    user = await db.get_user(message.from_user.id)
    if user:
        pass
    else:
        await db.add_user(message.from_user.id, message.from_user.username, message.from_user.first_name)

    items = await db.get_items_in_cart(message.from_user.id)
    if not items:
        await message.answer("🛒 Корзина пуста")
        return

    builder = InlineKeyboardBuilder()

    text = "🛒 <b>Ваша корзина:</b>\n\n"

    for item in items:
        builder.button(
            text=f"❌ {item['title']} - {item['quantity']}",
            callback_data=f"edit_{item['product_id']}"
        )

    builder.button(text="✅ Оформить", callback_data="checkout")

    builder.adjust(1)
    await message.answer(text=text, reply_markup=builder.as_markup(), parse_mode="HTML")


@cart_router.callback_query(F.data.startswith("edit_"))
async def show_cart_callback(callback: CallbackQuery):
    data = callback.data.split("_")
    if len(data) < 2 or not data[1].isdigit():
        await callback.answer("Ошибка данных!")
        return

    product_id = int(data[1])
    builder = InlineKeyboardBuilder()

    builder.button(text="🗑 Удалить товар", callback_data=f"DelCard_{product_id}")
    builder.button(text="⬅️ Назад", callback_data="open_cart")

    await callback.message.edit_text(
        "<i><b>Что сделать с этим товаром?</b></i>",
        parse_mode="HTML",
        reply_markup=builder.as_markup()
    )


@cart_router.callback_query(F.data.startswith("DelCard_"))
async def delete_card_from_cart(callback: CallbackQuery, db):
    product_id = callback.data.split("_")[1]
    builder = InlineKeyboardBuilder()
    builder.button(text="⬅️ Назад", callback_data="open_cart")
    await db.delete_item_from_cart(product_id, callback.from_user.id)
    await callback.message.edit_text("🎉 Ваш товар был успешно убран из корзины!", reply_markup=builder.as_markup())


@cart_router.callback_query(F.data == "checkout")
async def checkout_confirmation(callback: CallbackQuery, db):
    user_id = callback.from_user.id
    items = await db.get_items_in_cart(user_id)

    if not items:
        await callback.answer("🛒 Ваша корзина пуста!", show_alert=True)
        return

    total_price, _ = calculate_cart_total(items)

    builder = InlineKeyboardBuilder()
    builder.button(text="🚀 Подтвердить оформление", callback_data="confirm_order")
    builder.button(text="⬅️ Назад в корзину", callback_data="open_cart")
    builder.adjust(1)

    await callback.message.edit_text(
        text=f"❓ <b>Вы уверены, что хотите оформить заказ?</b>\n\n💰 Сумма к оплате: <b>{total_price:.2f} BYN</b>",
        reply_markup=builder.as_markup(),
        parse_mode="HTML"
    )


def calculate_cart_total(items):
    total_price = 0.0
    products_text = ""

    for item in items:
        item_total = float(item['price']) * int(item['quantity'])
        total_price += item_total
        products_text += f"• {item['title']} x{item['quantity']} ({item_total:.2f} BYN)\n"

    return total_price, products_text.strip()


@cart_router.callback_query(F.data == "confirm_order")
async def accept_order(callback: CallbackQuery, db, bot: Bot):
    user_id = callback.from_user.id
    items = await db.get_items_in_cart(user_id)
    total_price, products_text = calculate_cart_total(items)

    await db.add_order(user_id, products_text, total_price)
    await db.add_total_price_and_order(total_price, user_id)
    await db.clear_cart(user_id)

    success_text = (
        "🎉 <b>Заказ успешно оформлен!</b>\n\n"
        f"📋 <b>Ваш заказ:</b>\n{products_text}\n"
        f"💰 <b>Итого к оплате: {total_price:.2f} BYN</b>\n\n"
        "Наш менеджер уже начал его сборку! Спасибо, что выбрали PizzaFox 🦊🍕"
    )

    await callback.message.edit_text(text=success_text, parse_mode="HTML")
    await callback.answer("Заказ подтвержден!")

    try:
        pdf_file = await asyncio.to_thread(generate_pdf, callback.from_user.id, items, total_price)
        document = FSInputFile(pdf_file)
        await callback.message.reply_document(document=document, caption="🧾 Ваш электронный чек")

        if os.path.exists(pdf_file):
            os.remove(pdf_file)

    except Exception as e:
        print(f"Ошибка при генерации или отправке PDF: {e}")

    username = f"@{callback.from_user.username}" if callback.from_user.username else "Нет юзернейма"
    admin_send = (
        "🚨 <b>У вас новый заказ!</b>\n"
        "━━━━━━━━━━━━━━━━━━━━━\n"
        f"👤 <b>Покупатель:</b> {callback.from_user.first_name} ({username})\n"
        f"🆔 <b>ID:</b> <code>{user_id}</code>\n"
        "━━━━━━━━━━━━━━━━━━━━━\n"
        f"📋 <b>Состав заказа:</b>\n{products_text}\n"
        f"💰 <b>Стоимость заказа: {total_price:.2f} BYN</b>"
    )

    await bot.send_message(config.admin_id, text=admin_send, parse_mode="HTML")


@cart_router.callback_query(F.data.startswith("buy_"))
async def add_to_cart(callback: CallbackQuery, db):
    product_id = callback.data.split("_")[1]
    await db.add_to_cart(callback.from_user.id, product_id)
    await callback.answer("🎉 Товар успешно добавлен!")
