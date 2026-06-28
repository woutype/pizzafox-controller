class OrderCommands:
    def __init__(self):
        self.pool = None

    async def add_order(self, user_id, products_text, total_price):
        async with self.pool.acquire() as conn:
            await conn.execute("""
                INSERT INTO orders (user_id, products_text, total_price)
                VALUES ($1, $2, $3);
            """, user_id, products_text, total_price)

    async def add_total_price_and_order(self, price, user_id):
        async with self.pool.acquire() as conn:
            await conn.execute("""
                UPDATE users SET
                    total_spent = total_spent + $1,
                    total_orders = total_orders + 1
                WHERE user_id = $2;
            """, float(price), int(user_id))
