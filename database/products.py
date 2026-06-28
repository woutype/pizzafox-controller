class ProductCommands:
    def __init__(self):
        self.pool = None

    async def add_products_bulk(self, products_data):
        async with self.pool.acquire() as conn:
            await conn.executemany("""
                INSERT INTO products (product_id, title, price, description, image_url, category)
                VALUES ($1, $2, $3, $4, $5, $6)
                ON CONFLICT (product_id)
                DO UPDATE SET
                    title = EXCLUDED.title,
                    price = EXCLUDED.price,
                    description = EXCLUDED.description,
                    image_url = EXCLUDED.image_url,
                    category = EXCLUDED.category;
            """, products_data)

    async def get_product(self, product_id):
        async with self.pool.acquire() as conn:
            return await conn.fetchrow("""
                SELECT product_id, title, price, description, image_url, category
                FROM products WHERE product_id = $1;
            """, product_id)

    async def get_products_by_category(self, category):
        async with self.pool.acquire() as conn:
            return await conn.fetch("""
                SELECT product_id, title, price, description, image_url, category
                FROM products WHERE category = $1;
            """, category)
