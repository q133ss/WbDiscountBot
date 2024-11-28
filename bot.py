from flask import Flask, request, jsonify
from threading import Thread
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler
from handlers import start, button, balance, buyback_balance, ruble_balance, products, ads
from config import API_TOKEN
from db import get_chat_id_by_key
import asyncio

# Инициализация Telegram бота
tg_app = Application.builder().token(API_TOKEN).build()

# Flask-сервер
flask_app = Flask(__name__)

async def send_telegram_message(chat_id, message_text, button_text=None, button_url=None):
    """Асинхронная отправка сообщения в Telegram с кнопкой (если указана)."""
    if button_text and button_url:
        keyboard = [[InlineKeyboardButton(button_text, url=button_url)]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await tg_app.bot.send_message(chat_id=chat_id, text=message_text, reply_markup=reply_markup, parse_mode="HTML")
    else:
        await tg_app.bot.send_message(chat_id=chat_id, text=message_text, parse_mode="HTML")

@flask_app.route('/send-notification', methods=['POST'])
def send_notification():
    data = request.json
    key = data.get('key')  # Получаем ключ пользователя из запроса
    message_text = data.get('message')
    button_text = data.get('buttonText')
    button_url = data.get('buttonUrl')

    # Получаем chat_id по ключу
    chat_id = get_chat_id_by_key(key)

    if chat_id:
        try:
            print(f"Sending message to {chat_id}: {message_text}")

            # Отправка сообщения асинхронно
            asyncio.run(send_telegram_message(chat_id, message_text, button_text, button_url))
            
            return jsonify({"status": "success", "chatId": chat_id, "message": "Уведомление отправлено"})
        except Exception as e:
            return jsonify({"status": "error", "message": str(e)}), 500
    else:
        return jsonify({"status": "error", "message": "Пользователь не найден"}), 404

# Запуск Flask в отдельном потоке
def run_flask():
    flask_app.run(host='0.0.0.0', port=5000)

# Запуск Telegram бота и Flask
def run_flask_bot():
    # Запуск Flask-сервера в отдельном потоке
    Thread(target=run_flask).start()

    # Добавляем обработчики команд и колбэков для бота
    tg_app.add_handler(CommandHandler("start", start))
    tg_app.add_handler(CallbackQueryHandler(button, pattern='^profile$'))
    tg_app.add_handler(CallbackQueryHandler(balance, pattern='^balance$'))
    tg_app.add_handler(CallbackQueryHandler(buyback_balance, pattern='^buyback_balance$'))
    tg_app.add_handler(CallbackQueryHandler(ruble_balance, pattern='^ruble_balance$'))
    tg_app.add_handler(CallbackQueryHandler(products, pattern='^products$'))
    tg_app.add_handler(CallbackQueryHandler(ads, pattern='^ads$'))

    # Запускаем бота
    tg_app.run_polling()