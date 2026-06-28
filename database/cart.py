class CartCommands:
    def __init__(self):
        self.pool = None

    async def add_to_cart(self, user_id, product_id):
        async with self.pool.acquire() as conn:
            await conn.execute("""
                INSERT INTO cart (user_id, product_id, quantity) VALUES ($1, $2, 1)
                ON CONFLICT (user_id, product_id) DO UPDATE SET
                quantity = cart.quantity + 1;
            """, int(user_id), int(product_id))

    async def get_items_in_cart(self, user_id):
        async with self.pool.acquire() as conn:
            return await conn.fetch("""
                SELECT
                    cart.product_id,
                    products.title,
                    products.price,
                    cart.quantity
                FROM cart
                JOIN products ON cart.product_id = products.product_id
                WHERE cart.user_id = $1;
            """, int(user_id))

    async def delete_item_from_cart(self, product_id, user_id):
        async with self.pool.acquire() as conn:
            await conn.execute("""
                UPDATE cart SET quantity = quantity - 1
                WHERE user_id = $1 AND product_id = $2;
            """, int(user_id), int(product_id))

            await conn.execute("""
                DELETE FROM cart
                WHERE user_id = $1 AND product_id = $2 AND quantity <= 0;
            """, int(user_id), int(product_id))

    @staticmethod
    async def clear_cart_transactional(conn, user_id):
        await conn.execute(
            "DELETE FROM cart WHERE user_id = $1;",
            int(user_id))