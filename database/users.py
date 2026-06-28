class UserCommands:
    def __init__(self):
        self.pool = None

    async def add_user(self, user_id, username, first_name):
        async with self.pool.acquire() as conn:
            await conn.execute("""
                INSERT INTO users (user_id, username, first_name)
                VALUES ($1, $2, $3)
                ON CONFLICT (user_id) DO NOTHING;
            """, user_id, username, first_name)

    async def get_user(self, user_id):
        async with self.pool.acquire() as conn:
            return await conn.fetchrow("""
                SELECT username, first_name, total_orders, total_spent
                FROM users WHERE user_id = $1;
            """, int(user_id))
