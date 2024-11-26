import sqlite3

# Функция для создания таблицы user_keys, если она не существует
def create_table():
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_keys (
            chat_id INTEGER PRIMARY KEY,
            key TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

# Функция для получения ключа по chat_id
def get_user_key(chat_id):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute("SELECT key FROM user_keys WHERE chat_id = ?", (chat_id,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else None

# Функция для добавления нового пользователя в базу данных
def save_user_key(chat_id, key):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    # Проверяем, существует ли уже пользователь с таким chat_id
    cursor.execute("SELECT * FROM user_keys WHERE chat_id = ?", (chat_id,))
    result = cursor.fetchone()

    if result:
        # Если пользователь существует, обновляем ключ
        cursor.execute("UPDATE user_keys SET key = ? WHERE chat_id = ?", (key, chat_id))
    else:
        # Если пользователя нет, вставляем новый
        cursor.execute("INSERT INTO user_keys (chat_id, key) VALUES (?, ?)", (chat_id, key))

    conn.commit()
    conn.close()
