from db import create_table  # Импорт функции для создания таблицы
from bot import run_flask_bot  # Импорт функции из bot.py

if __name__ == '__main__':
    create_table()  # Создание таблицы в базе данных, если её нет
    run_flask_bot()  # Запуск Telegram бота и Flask-сервера