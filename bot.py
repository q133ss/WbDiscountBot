import asyncio
from quart import Quart, request, jsonify
from aiohttp import ClientSession
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler
from handlers import start, button, balance, buyback_balance, ruble_balance, products, ads
from config import API_TOKEN
from db import get_chat_id_by_key


# Инициализация Telegram бота
tg_app = Application.builder().token(API_TOKEN).build()

# Quart-сервер
quart_app = Quart(__name__)

async def send_telegram_message(chat_id, message_text, button_text=None, button_url=None):
    """Асинхронная отправка сообщения в Telegram с кнопкой (если указана)."""
    if button_text and button_url:
        keyboard = [[InlineKeyboardButton(button_text, url=button_url)]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await tg_app.bot.send_message(chat_id=chat_id, text=message_text, reply_markup=reply_markup, parse_mode="HTML")
    else:
        await tg_app.bot.send_message(chat_id=chat_id, text=message_text, parse_mode="HTML")

async def handle_send_notification(data):
    """Обработка отправки уведомлений, асинхронно."""
    key = data.get('key')
    message_text = data.get('message')
    button_text = data.get('buttonText')
    button_url = data.get('buttonUrl')

    # Получаем chat_id по ключу
    chat_id = get_chat_id_by_key(key)

    if chat_id:
        try:
            print(f"Sending message to {chat_id}: {message_text}")

            # Отправка сообщения в Telegram
            await send_telegram_message(chat_id, message_text, button_text, button_url)
            return {"status": "success", "chatId": chat_id, "message": "Уведомление отправлено"}
        except Exception as e:
            print("Ошибка: " + str(e))
            return {"status": "error", "message": str(e)}
    else:
        return {"status": "error", "message": "Пользователь не найден"}

@quart_app.route('/send-notification', methods=['POST'])
async def send_notification():
    """API-метод для отправки уведомлений."""
    data = await request.json  # Получаем данные из POST-запроса
    response = await handle_send_notification(data)
    return jsonify(response)

# Запуск Telegram бота и Quart-сервера
def run_quart_bot():
    loop = asyncio.get_event_loop()

    # Запускаем сервер Quart в асинхронном режиме
    loop.create_task(quart_app.run_task(host='0.0.0.0', port=5000))

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