import aiosqlite


DB_NAME = 'quiz_bot.db'

async def get_users_score(pk: int) -> int:
    """
    Функция возвращает данные статистики по итогам оветов пользователя.
    :param pk: int
    :return: results
    """
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute("SELECT score FROM users WHERE user_id = ?", (pk,)) as cursor:
            results = await cursor.fetchone()
            if results is not None:
                return results[0]
            else:
                return 0


async def update_quiz_index(user_id, index):
    """
    Создаем соединение с базой данных (если она не существует, она будет создана).
    Вставляем новую запись или заменяем ее, если с данным user_id уже существует.
    Сохраняем изменения.
    :param user_id: int
    :param index: int
    :return: None
    """
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute('INSERT OR REPLACE INTO quiz_state (user_id, question_index) VALUES (?, ?)', (user_id, index))
        await db.commit()


async def get_quiz_index(user_id):
    """
    Получаем запись для заданного пользователя,
    Возвращаем результат.
    :param user_id: int
    :return: results
    """
    # Подключаемся к базе данных
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute('SELECT question_index FROM quiz_state WHERE user_id = (?)', (user_id,)) as cursor:
            results = await cursor.fetchone()
            if results is not None:
                return results[0]
            else:
                return 0

async def update_users_score(pk: int, score: int) -> None:
    """
    Функция обновляет данные в БД, добавляет очки правильных ответов.
    :param pk: int
    :param score: int
    :return: None
    """
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("INSERT INTO users (user_id, score) VALUES (?, ?) ON CONFLICT(user_id) DO UPDATE SET score = "
                         "excluded.score", (pk, score))
        await db.commit()


async def create_table():
    """
    Функция создает соединение с базой данных (если она не существует, она будет создана);
    создает таблицу quiz_state с полями user_id и question_index;
    создает таблицу users с полями user_id и score;
    сохраняет изменения.
    :return: None
    """
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute(
            '''CREATE TABLE IF NOT EXISTS quiz_state (user_id INTEGER PRIMARY KEY, question_index INTEGER)''')
        await db.execute(
            '''CREATE TABLE IF NOT EXISTS users (user_id INTEGER PRIMARY KEY, score INTEGER)''')
        await db.commit()
