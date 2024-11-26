from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext
import requests
from db import get_user_key, save_user_key
from config import API_URL, PROFILE_URL

async def getChatId(update):
    if update.message:
        return update.message.chat.id
    elif update.callback_query:
        return update.callback_query.message.chat.id
    else:
        # Если нет ни сообщения, ни callback_query, то возвращаем ошибку
        await update.answer("Не удалось получить данные.")
        return

# Обработчик команды /start
async def start(update: Update, context: CallbackContext):
    chat_id = update.message.chat.id

    # Проверяем, передан ли параметр
    if context.args:
        key = context.args[0]  # Получаем переданный key
        save_user_key(chat_id, key)  # Сохраняем key в базу данных
        await update.message.reply_text("Вы успешно вошли")
    else:
        await update.message.reply_text("Вход не удался, попробуйте еще раз.")

    # Создаем кнопки
    keyboard = [
        [InlineKeyboardButton("Мой профиль", callback_data='profile')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text('Добро пожаловать!', reply_markup=reply_markup)

# Обработчик нажатия на кнопки
async def button(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()

    if query.data == 'profile':
        chat_id = query.message.chat.id
        key = get_user_key(chat_id)

        if key:
            # Отправляем GET запрос на сервер с ключом
            response = requests.get(API_URL + "/tg/user?key="+key)

            if response.status_code == 200:
                user_data = response.json().get("user", {})
                 # Достаём нужные поля
                name = user_data.get('name', 'Не указано')
                balance = user_data.get('balance', 0)  # Если в будущем будет баланс
                inn = user_data.get('inn', 'Не указано')
                shop_name = user_data.get('shopName', 'Не указано')
                
                profile_info = (f"Имя: {name}\n"
                                f"ИНН: {inn}\n"
                                f"Магазин: {shop_name}")

                keyboard = [
                    [InlineKeyboardButton("Баланс", callback_data='balance')],
                    [InlineKeyboardButton("Товары", callback_data='products')],
                    [InlineKeyboardButton("Объявления", callback_data='ads')],
                    [InlineKeyboardButton("Перейти в профиль", url=f"{PROFILE_URL}")]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                await query.edit_message_text(text=profile_info, reply_markup=reply_markup)
            else:
                print(response)
                await query.edit_message_text(text="Не удалось получить информацию с сервера.")
        else:
            await query.edit_message_text(text="Ваш ключ не найден в базе данных.")


# Обработчики для кнопок (баланс, товары, объявления)
async def balance(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()

    keyboard = [
        [InlineKeyboardButton("Баланс выкупов", callback_data='buyback_balance')],
        [InlineKeyboardButton("Рублёвый баланс", callback_data='ruble_balance')],
        [InlineKeyboardButton("Вернуться в меню", callback_data='profile')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(text="Выберите тип баланса:", reply_markup=reply_markup)

async def buyback_balance(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()

    chat_id = query.message.chat.id
    key = get_user_key(chat_id)

    if key:
        # Отправляем GET запрос на сервер с ключом
        response = requests.get(API_URL + "/tg/user?key="+key)

        if response.status_code == 200:
            user_data = response.json().get("user", {})
            payback = user_data.get('payback', 0)
            
            profile_info = (f"Баланс выкупов: {payback}")

            keyboard = [
                [InlineKeyboardButton("Пополнить", callback_data='recharge')],
                [InlineKeyboardButton("Вернуться в меню", callback_data='profile')]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.edit_message_text(text=profile_info, reply_markup=reply_markup)
        else:
            print(response)
            await query.edit_message_text(text="Не удалось получить информацию с сервера.")
    else:
        await query.edit_message_text(text="Ваш ключ не найден в базе данных.")

async def ruble_balance(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()
    
    chat_id = query.message.chat.id
    key = get_user_key(chat_id)

    if key:
        # Отправляем GET запрос на сервер с ключом
        response = requests.get(API_URL + "/tg/user?key="+key)

        if response.status_code == 200:
            user_data = response.json().get("user", {})
            balance = user_data.get('balance', 0)
            
            profile_info = (f"Баланс рублёвый: {balance}")

            keyboard = [
                [InlineKeyboardButton("Пополнить", callback_data='recharge')],
                [InlineKeyboardButton("Вернуться в меню", callback_data='profile')]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.edit_message_text(text=profile_info, reply_markup=reply_markup)
        else:
            print(response)
            await query.edit_message_text(text="Не удалось получить информацию с сервера.")
    else:
        await query.edit_message_text(text="Ваш ключ не найден в базе данных.")

# Функция для создания кнопок товаров с подсветкой статуса
def create_product_buttons(products):
    buttons = []
    for product in products:
        button_text = f"{product['title']} - {product['price']}₽"
        url = f"https://wbdiscount.pro/user/announcement/{product['id']}"  # Ссылка на товар

        # Подсветка статуса товара
        if product['status']:
            button = InlineKeyboardButton(text=f"✅ {button_text}", url=url, callback_data=f"product_{product['id']}")
        else:
            button = InlineKeyboardButton(text=f"❌ {button_text}", url=url, callback_data=f"product_{product['id']}")
        buttons.append([button])
    return InlineKeyboardMarkup(buttons)

# Функция пагинации
def paginate(products, page=1, page_size=1000):
    start = (page - 1) * page_size
    end = page * page_size
    return products[start:end]


# Обработчик команды products
async def products(update: Update, context: CallbackContext):
    chat_id = await getChatId(update)
    key = get_user_key(chat_id)

    if key:
        response = requests.get(f"{API_URL}/product/getAll?userId={key}")
        print(f"{API_URL}/product/getAll?userId={key}")

        if response.status_code == 200:
            data = response.json()
            products = data.get('productsWithUrls', [])
            page = int(context.args[0]) if context.args else 1

            # Пагинация
            products_on_page = paginate(products, page)

            for product in products_on_page:
                title = product.get('title', 'Без названия')
                buybacks = product.get('buybacks', 0)
                purchases = product.get('purchases', 0)
                views = product.get('views', 0)
                conversation = product.get('conversation', 0)
                status = "Активен" if product.get('status') else "Неактивен"
                
                # Получаем первое изображение из массива
                images = product.get('images', [])
                photo_url = images[0] if images else 'https://example.com/default_image.jpg'  # Заглушка, если изображение отсутствует
                
                # Формируем текст сообщения
                message_text = (
                    f"<b>{title}</b>\n"
                    f"📦 Выкупы: {buybacks}\n"
                    f"🛒 Покупки: {purchases}\n"
                    f"👁️ Просмотры: {views}\n"
                    f"💬 Отклики: {conversation}\n"
                    f"🔘 Статус: {status}"
                )
                
                try:
                    await context.bot.send_photo(
                        chat_id=chat_id,
                        photo=photo_url,
                        caption=message_text,
                        parse_mode='HTML'
                    )
                except Exception as e:
                    await context.bot.send_message(chat_id=chat_id, text="Ошибка при загрузке изображения.")
                    print(f"Error sending photo: {e}")


            # Кнопки навигации
            navigation_buttons = [
                [InlineKeyboardButton("🔙 Вернуться в меню", callback_data='profile')]
            ]

            reply_markup = InlineKeyboardMarkup(navigation_buttons)
            await context.bot.send_message(chat_id=chat_id, text="Навигация по товарам:", reply_markup=reply_markup)

        else:
            await update.callback_query.edit_message_text("Не удалось получить информацию с сервера.")
    else:
        await update.callback_query.edit_message_text("Ваш ключ не найден в базе данных.")


async def ads(update: Update, context: CallbackContext):
    chat_id = await getChatId(update)
    key = get_user_key(chat_id)

    if key:
        # Запрос на получение объявлений
        response = requests.get(f"{API_URL}/tg/announcement/?userId={key}")
        print(f"{API_URL}/tg/announcement/?userId={key}")

        if response.status_code == 200:
            data = response.json()
            announcements = data.get('announcements', [])

            # Перебор всех объявлений и отправка каждого как отдельного сообщения с фото
            for ad in announcements:
                photo_url = ad['Product']['images'][0]['url']  # Берем первую картинку товара
                title = ad['title']
                price = ad['price']
                cashback = ad['cashback']

                # Текст сообщения
                message_text = (
                    f"<b>{title}</b>\n"
                    f"💰 Цена: {price} руб.\n"
                    f"🎁 Кешбэк: {cashback} руб."
                )

                # Кнопка для детального просмотра или заказа
                keyboard = [[InlineKeyboardButton("Посмотреть объявление", url=f"https://wbdiscount.pro/user/announcement/{ad['id']}")]]
                reply_markup = InlineKeyboardMarkup(keyboard)

                # Отправка сообщения с фото и кнопкой
                await context.bot.send_photo(
                    chat_id=chat_id,
                    photo=photo_url,
                    caption=message_text,
                    reply_markup=reply_markup,
                    parse_mode='HTML'
                )

            # Кнопка возврата после всех объявлений
            return_button = [[InlineKeyboardButton("Вернуться в меню", callback_data='profile')]]
            await context.bot.send_message(chat_id=chat_id, text="🔙 Вернуться в меню:", reply_markup=InlineKeyboardMarkup(return_button))
            
        else:
            await update.callback_query.edit_message_text("Не удалось получить информацию с сервера.")
    else:
        await update.callback_query.edit_message_text("Ваш ключ не найден в базе данных.")