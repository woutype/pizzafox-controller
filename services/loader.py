import asyncio
import aiohttp

url_drinks = "https://pzz.by/api/v1/drinks?filter=pizzeria_type:pizzeria,is_alcoholic:0&order=position:asc"
url_desserts = "https://pzz.by/api/v1/desserts?filter=pizzeria_type:pizzeria&order=position:asc"
url_snacks = "https://pzz.by/api/v1/snacks?load=modifications&filter=meal_only:0,parent_id:is:null&order=position:asc"
url_pizza = "https://pzz.by/api/v1/pizzas?load=ingredients,modifications,filters&filter=meal_only:0,parent_id:is:null&order=position:asc"


async def get_data(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            if resp.status == 404:
                return None
            return await resp.json()


async def get_drinks(db):
    drinks_json = await get_data(url_drinks)
    drinks_data = drinks_json["response"]["data"]
    products_to_add = []

    for item in drinks_data:
        products_to_add.append((
            item["id"], item["title_inner"], item["price"] / 10000,
            item["producer_country"], item["photo_small"], "drinks"
        ))

    await db.add_products_bulk(products_to_add)
    print("✅ Напитки загружены!")


async def get_desserts(db):
    desserts_json = await get_data(url_desserts)
    desserts_data = desserts_json["response"]["data"]
    products_to_add = []

    for item in desserts_data:
        products_to_add.append((
            item["id"], item["title"], item["price"] / 10000,
            item["amount"], item["photo_small"], "desserts"
        ))

    await db.add_products_bulk(products_to_add)
    print("✅ Десерты загружены!")


async def get_snacks(db):
    snacks_json = await get_data(url_snacks)
    snacks_data = snacks_json["response"]["data"]
    products_to_add = []

    for item in snacks_data:
        products_to_add.append((
            item["id"], item["title"], item["big_price"] / 10000,
            item["anonce"] + " " + item["big_amount"], item["photo_small"], "snacks"
        ))

    await db.add_products_bulk(products_to_add)
    print("✅ Закуски загружены!")


async def get_pizza(db):
    pizza_json = await get_data(url_pizza)
    pizza_data = pizza_json["response"]["data"]

    products_to_add = []

    for item in pizza_data:
        product_id = item["id"]
        title = item["title"]
        price = item["big_price"] / 10000
        description = item["anonce"]
        image_url = item["photo_small"]
        category = "pizza"

        products_to_add.append((product_id, title, price, description, image_url, category))

    await db.add_products_bulk(products_to_add)
    print("✅ Пиццы загружены!")


async def check_all_products(db):
    interval = 60 * 60 * 24
    while True:
        try:
            print("Начинаем заполнение базы данных...")
            await get_pizza(db)
            await get_desserts(db)
            await get_drinks(db)
            await get_snacks(db)
            print("\n🎉 Все категории успешно импортированы в PostgreSQL!")
            await asyncio.sleep(interval)
        except Exception as e:
            print(f"Ошибка при обновлении товаров: {e}")
            await asyncio.sleep(60 * 5)
