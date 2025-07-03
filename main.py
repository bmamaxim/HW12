import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters.command import Command
from aiogram import types
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from aiogram import F
from dotenv import load_dotenv
import os
from reader import quiz_data
from functions import get_question, new_quiz
from db_utils import (get_users_score,
                      update_quiz_index,
                      get_quiz_index,
                      update_users_score,
                      create_table)


load_dotenv()

# Включаем логирование, чтобы не пропустить важные сообщения
logging.basicConfig(level=logging.INFO)

# Замените "YOUR_BOT_TOKEN" на токен, который вы получили от BotFather
API_TOKEN = os.getenv("BOT_TOKEN")

# Объект бота
bot = Bot(token=API_TOKEN)
# Диспетчер
dp = Dispatcher()


@dp.callback_query(F.data == "right_answer")
async def right_answer(callback: types.CallbackQuery) -> None:
    """
    Функция обрабатывает верные ответы в чат боте,
    записывает ответы в базу данных, выводит в чат
    результаты викторины.
    :param callback: CallbackQuery
    :return: None
    """
    await callback.bot.edit_message_reply_markup(
        chat_id=callback.from_user.id,
        message_id=callback.message.message_id,
        reply_markup=None
    )

    await callback.message.answer("Верно!")
    current_question_index = await get_quiz_index(callback.from_user.id)
    current_score = await get_users_score(callback.from_user.id)
    # Обновление номера текущего вопроса в базе данных
    current_question_index += 1
    current_score += 1
    await update_quiz_index(callback.from_user.id, current_question_index)
    await update_users_score(callback.from_user.id, current_score)

    if current_question_index < len(quiz_data):
        await get_question(callback.message, callback.from_user.id)
    else:
        await callback.message.answer(f"Это был последний вопрос. Квиз завершен!\nВаш результат: {current_score} "
                                      f"верных ответов")


@dp.callback_query(F.data == "wrong_answer")
async def wrong_answer(callback: types.CallbackQuery) -> None:
    """
    Функция обрабатывает не верные ответы в чат боте,
    записывает ответы в базу данных, выводит в чат
    результаты викторины.
    :param callback: CallbackQuery
    :return: None
    """
    await callback.bot.edit_message_reply_markup(
        chat_id=callback.from_user.id,
        message_id=callback.message.message_id,
        reply_markup=None
    )
    # Получение текущего вопроса из словаря состояний пользователя
    current_score = await get_users_score(callback.from_user.id)
    current_question_index = await get_quiz_index(callback.from_user.id)
    correct_option = quiz_data[current_question_index]['correct_option']
    await callback.message.answer(
        f"Неправильно. Правильный ответ: {quiz_data[current_question_index]['options'][correct_option]}")
    # Обновление номера текущего вопроса в базе данных
    current_question_index += 1
    await update_quiz_index(callback.from_user.id, current_question_index)
    await update_users_score(callback.from_user.id, current_score)
    if current_question_index < len(quiz_data):
        await get_question(callback.message, callback.from_user.id)
    else:
        await callback.message.answer(f"Это был последний вопрос. Квиз завершен!\nВаш результат: {current_score} "
                                      f"верных ответов")


@dp.message(Command("start"))
async def cmd_start(message: types.Message) -> None:
    """
    Хэндлер на команду /start.
    :param message: Message
    :return: None
    """
    builder = ReplyKeyboardBuilder()
    builder.add(types.KeyboardButton(text="Начать игру"))
    await message.answer("Добро пожаловать в квиз!", reply_markup=builder.as_markup(resize_keyboard=True))


@dp.message(F.text == "Начать игру")
@dp.message(Command("quiz"))
async def cmd_quiz(message: types.Message) -> None:
    """
    Хэндлер на команду /quiz.
    :param message: Message
    :return: None
    """
    await message.answer(f"Давайте начнем квиз!")
    await new_quiz(message)


@dp.message(Command("help"))
async def cmd_start(massage: types.Message) -> None:
    """
    Хэндлер на команду /help.
    :param massage: Message
    :return: None
    """
    await massage.answer(f"Команды бота:\n/start - начать взаимодействие с ботом\n/help - открыть помощь\n/quiz - "
                         "начать игру")


async def main():
    """
    Запуск процесса поллинга новых апдейтов,
    Запускаем создание таблицы базы данных.
    :return:
    """
    await create_table()

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
