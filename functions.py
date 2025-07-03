from aiogram import types, Dispatcher
from aiogram.utils.keyboard import InlineKeyboardBuilder
from reader import quiz_data
from db_utils import (update_quiz_index, 
                      update_users_score, 
                      get_quiz_index)


dp = Dispatcher()


def generate_options_keyboard(answer_options, right_answer):
    """
    Функция обработки ответов.
    :param answer_options: str
    :param right_answer: str
    :return: str
    """
    builder = InlineKeyboardBuilder()
    for option in answer_options:
        builder.add(types.InlineKeyboardButton(
            text=option,
            callback_data="right_answer" if option == right_answer else "wrong_answer")
        )

    builder.adjust(1)
    return builder.as_markup()


async def get_question(message, user_id):
    """
    Получение текущего вопроса из словаря состояний пользователя
    :param message: str
    :param user_id: int
    :return: None
    """
    current_question_index = await get_quiz_index(user_id)
    correct_index = quiz_data[current_question_index]["correct_option"]
    opts = quiz_data[current_question_index]["options"]
    kb = generate_options_keyboard(opts, opts[correct_index])
    await message.answer(f"{quiz_data[current_question_index]["question"]}", reply_markup=kb)


async def new_quiz(message):
    """
    Функция обновляет данные в БД.
    Передает данные в функцию get_question.
    :param message: str
    :return: None
    """
    user_id = message.from_user.id
    current_question_index = 0
    score = 0
    await update_quiz_index(user_id, current_question_index)
    await update_users_score(user_id, score)
    await get_question(message, user_id)
