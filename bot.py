from telegram.ext import Application, CommandHandler, CallbackQueryHandler
from handlers import start, button, balance, buyback_balance, ruble_balance, products, ads
from config import API_TOKEN

def main():
    app = Application.builder().token(API_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button, pattern='^profile$'))
    app.add_handler(CallbackQueryHandler(balance, pattern='^balance$'))
    app.add_handler(CallbackQueryHandler(buyback_balance, pattern='^buyback_balance$'))
    app.add_handler(CallbackQueryHandler(ruble_balance, pattern='^ruble_balance$'))
    app.add_handler(CallbackQueryHandler(products, pattern='^products$'))
    app.add_handler(CallbackQueryHandler(ads, pattern='^ads$'))

    app.run_polling()

if __name__ == '__main__':
    main()