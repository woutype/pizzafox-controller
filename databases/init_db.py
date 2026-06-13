import asyncpg
from config import config


class Database:
    def __init__(self):
        self.pool = None

    async def connect(self):
        self.pool = await asyncpg.create_pool(
            user=config.user,
            password=config.password,
            host=config.host,
            database=config.database,
            port=config.port
        )
        await self.create_tables()

    async def create_tables(self):
        async with self.pool.acquire() as conn:
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    user_id BIGINT PRIMARY KEY,
                    username TEXT,
                    first_name TEXT,
                    total_orders INTEGER DEFAULT 0,
                    total_spent REAL DEFAULT 0
                );
            """)
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS products (
                    id SERIAL PRIMARY KEY,
                    product_id INTEGER UNIQUE,
                    title TEXT,
                    price REAL,
                    description TEXT,
                    image_url TEXT,
                    category TEXT
                );
            """)
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS orders (
                    order_id SERIAL PRIMARY KEY,
                    user_id BIGINT NOT NULL,
                    products_text TEXT NOT NULL,
                    total_price REAL NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS cart (
                    cart_id SERIAL PRIMARY KEY,
                    user_id BIGINT NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
                    product_id INTEGER NOT NULL REFERENCES products(product_id) ON DELETE CASCADE,
                    quantity INTEGER DEFAULT 1
                );
            """)

    async def add_product(self, product_id, title, price, description, image_url, category):
        async with self.pool.acquire() as conn:
            query = """
                INSERT INTO products (product_id, title, price, description, image_url, category) 
                VALUES ($1, $2, $3, $4, $5, $6)
                ON CONFLICT (product_id) 
                DO UPDATE SET 
                    title = EXCLUDED.title, 
                    price = EXCLUDED.price, 
                    description = EXCLUDED.description, 
                    image_url = EXCLUDED.image_url, 
                    category = EXCLUDED.category;
            """
            await conn.execute(query, product_id, title, price, description, image_url, category)

    async def get_products(self, product_id):
        async with self.pool.acquire() as conn:
            query = """
                SELECT product_id, title, price, description, image_url, category 
                FROM products WHERE product_id = $1;
            """
            return await conn.fetchrow(query, product_id)

    async def get_user(self, user_id):
        async with self.pool.acquire() as conn:
            query = """
                SELECT username, first_name, total_orders, total_spent FROM users WHERE user_id = $1;
            """
            return await conn.fetchrow(query, int(user_id))

    async def add_user(self, user_id, username, first_name):
        async with self.pool.acquire() as conn:
            await conn.execute("""
                INSERT INTO users (user_id, username, first_name) 
                VALUES ($1, $2, $3)
                ON CONFLICT (user_id) DO NOTHING;
            """, user_id, username, first_name)

    async def get_products_by_category(self, category):
        async with self.pool.acquire() as conn:
            query = """
                SELECT product_id, title, price, description, image_url, category FROM products WHERE category = $1;
            """
            return await conn.fetch(query, category)

    async def add_to_cart(self, user_id, product_id):
        async with self.pool.acquire() as conn:
            query = """
                INSERT INTO cart (user_id, product_id, quantity) VALUES ($1, $2, 1)
                ON CONFLICT (user_id, product_id) DO UPDATE SET
                quantity = cart.quantity + 1;
            """
            await conn.execute(query, int(user_id), int(product_id))

    async def get_cart_item(self, product_id):
        async with self.pool.acquire() as conn:
            query = """
                SELECT
                    cart.product_id, products.title, products.price, cart.quantity
                FROM cart
                JOIN products ON cart.product_id = products.product_id
                WHERE cart.product_id = $1;
            """
            return await conn.fetchrow(query, product_id)

    async def get_items_in_cart(self, user_id: int):
        async with self.pool.acquire() as conn:
            query = """
                SELECT 
                    cart.product_id, 
                    products.title, 
                    products.price, 
                    cart.quantity
                FROM cart
                JOIN products ON cart.product_id = products.product_id
                WHERE cart.user_id = $1;
            """
            return await conn.fetch(query, int(user_id))

    async def delete_item_from_cart(self, product_id, user_id):
        async with self.pool.acquire() as conn:
            query = """
                UPDATE cart SET quantity = quantity - 1
                WHERE user_id = $1 AND product_id = $2;
            """
            await conn.execute(query, int(user_id), int(product_id))

            query = """
                DELETE FROM cart
                WHERE user_id = $1 AND product_id = $2 AND quantity <= 0;
            """
            await conn.execute(query, int(user_id), int(product_id))


    async def add_order(self, user_id, product_text, total_price):
        async with self.pool.acquire() as conn:
            query = """
                INSERT INTO orders (user_id, products_text, total_price) VALUES ($1, $2, $3);
            """
            await conn.execute(query, user_id, product_text, total_price)

    async def clear_cart(self, user_id):
        async with self.pool.acquire() as conn:
            await conn.execute("DELETE FROM cart WHERE user_id = $1;", int(user_id))

    async def get_simple_user(self, user_id: int):
        async with self.pool.acquire() as conn:
            query = """
                SELECT first_name, total_orders, total_spent FROM users WHERE user_id = $1
            """
            return await conn.fetchrow(query, int(user_id))

    async def add_total_price_and_order(self, price, user_id):
        async with self.pool.acquire() as conn:

            query = """
                UPDATE users SET 
                    total_spent = total_spent + $1,
                    total_orders = total_orders + 1
                WHERE user_id = $2;
            """

            await conn.execute(query, float(price), int(user_id))