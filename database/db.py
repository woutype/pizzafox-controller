import asyncpg

from config import config
from database.users import UserCommands
from database.products import ProductCommands
from database.cart import CartCommands
from database.orders import OrderCommands


class Database(UserCommands, ProductCommands, CartCommands, OrderCommands):
    def __init__(self):
        super().__init__()
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
                    total_spent NUMERIC(10, 2) DEFAULT 0
                );
            """)
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS products (
                    id SERIAL PRIMARY KEY,
                    product_id INTEGER UNIQUE,
                    title TEXT,
                    price NUMERIC(10, 2),
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
                    total_price NUMERIC(10, 2) NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS cart (
                    cart_id SERIAL PRIMARY KEY,
                    user_id BIGINT NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
                    product_id INTEGER NOT NULL REFERENCES products(product_id) ON DELETE CASCADE,
                    quantity INTEGER DEFAULT 1,
                    UNIQUE(user_id, product_id)
                );
            """)
