DATABASE_URL = 'postgresql://postgres:80156120189fap@localhost/workers'


import os

# Получение переменных окружения для безопасности и удобства управления конфигурациями
BOT_TOKEN = os.getenv("BOT_TOKEN", "7474061703:AAF9pQK_lpTDEEkIOkZ3ewaMNJbjNzJNFv8")  # Токен вашего бота из BotFather
DB_HOST = os.getenv("DB_HOST", "localhost")  # Хост базы данных
DB_PORT = os.getenv("DB_PORT", "5432")  # Порт базы данных, по умолчанию для PostgreSQL
DB_USER = os.getenv("DB_USER", "postgres")  # Имя пользователя базы данных
DB_PASS = os.getenv("DB_PASS", "80156120189fap")  # Пароль пользователя базы данных
DB_NAME = os.getenv("DB_NAME", "workers")  # Название базы данных

