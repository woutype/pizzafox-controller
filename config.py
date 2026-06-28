import os
from dotenv import load_dotenv
from dataclasses import dataclass

load_dotenv()


@dataclass
class Config:
    bot_token: str
    admin_id: int
    user: str
    password: str
    host: str
    database: str
    port: int


def load_config():
    bot_token = os.getenv("BOT_TOKEN")
    admin_id = os.getenv("ADMIN_ID")
    user = os.getenv("DB_USER")
    password = os.getenv("DB_PASSWORD")
    host = os.getenv("DB_HOST")
    database = os.getenv("DB_DATABASE")
    port = os.getenv("DB_PORT")

    if not bot_token:
        raise ValueError("Переменная BOT_TOKEN не найдена в файле .env")
    if not admin_id:
        raise ValueError("Переменная ADMIN_ID не найдена в файле .env")
    if not user:
        raise ValueError("Переменная DB_USER не найдена в файле .env")
    if not password:
        raise ValueError("Переменная DB_PASSWORD не найдена в файле .env")
    if not host:
        raise ValueError("Переменная DB_HOST не найдена в файле .env")
    if not database:
        raise ValueError("Переменная DB_DATABASE не найдена в файле .env")
    if not port:
        raise ValueError("Переменная DB_PORT не найдена в файле .env")

    return Config(
        bot_token=bot_token,
        admin_id=int(admin_id),
        user=user,
        password=password,
        host=host,
        database=database,
        port=int(port)
    )


config = load_config()
