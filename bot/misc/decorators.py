import datetime
import traceback
import logging
import os
import json

from .custom_types import BotTimer
from aiogram import types
from database.methods.select import get_user
from database.methods.insert import add_user


def rule_wrapper(rules: tuple):
    """Enables or disables the execution of the function depending on the rules passed."""

    def decorator(func):

        async def wrapper(*args):
            message: types.Message = args[0]
            # user_group = db_handler.get_user_info(message.from_user.id)
            user_group = 'admin'
            if user_group == 'banned':
                await message.reply('Кажется, вы забанены.')
            elif user_group in rules:
                await func(message)
            else:
                await message.reply(f'Ваша группа ({user_group}) не находится в числе разрешённых ({rules})')

        return wrapper

    return decorator


def time_wrapper(timeout: int = 5):
    """Enables (or disables) the execution of the function depending on the time passed.
    Also adds a timestamp for user"""

    def decorator(func):

        async def wrapper(*args, **kwargs):
            message: types.Message = args[0]
            bot_timer = BotTimer()
            __now = datetime.datetime.now().timestamp()
            __last_message_in = bot_timer.message_time_dict.get(message.from_id, 0)

            if __now > __last_message_in + timeout:
                await func(*args)
                bot_timer.message_time_dict[message.from_id] = __now
            else:
                __word = \
                    "секунд" if timeout in (0, 5, 6, 7, 8, 9, 10) else "секунды" if timeout in (2, 3, 4) else "секунда"
                await message.reply(f'С последнего сообщения должно пройти как минимум {timeout} {__word},'
                                    f' чтобы выполнить эту команду')

        return wrapper

    if isinstance(timeout, int):
        timeout = 10 if timeout > 10 else timeout
        return decorator
    else:
        function = timeout
        timeout = 0
        return decorator(function)


def start_wrapper(func):
    """/start wrapper"""

    async def wrapper(*args, **kwargs):
        logger: logging.Logger = logging.getLogger('BSEU Schedule')
        message: types.Message = args[0]
        user = get_user(message.from_id)
        if user is None:
            user = add_user(message)
            logger.debug(f'Add new user {user}')
        await func(*args, user)

    return wrapper


def callback_wrapper(func):
    """Remove Inline Markup in message"""

    async def wrapper(*args, **kwargs):
        logger: logging.Logger = logging.getLogger('BSEU Schedule')
        callback_query: types.CallbackQuery = args[0]
        message: types.Message = callback_query.message
        __inline_dict = {}
        __inline_general_list = callback_query.message.reply_markup.inline_keyboard
        for __inline_list in __inline_general_list:
            for __item in __inline_list:
                __inline_dict[__item['callback_data']] = __item['text']
        __action = __inline_dict.get(callback_query.data, 'Не установлено')
        await message.edit_text(
            text=f'{message.text}\n\nВыбран вариант "{__action}"', reply_markup=None
        )
        logger.debug(
            f'Callback {callback_query} from @{callback_query.from_user.username} {callback_query.from_user.id}'
        )
        await func(callback_query)

    return wrapper


def log(func):
    """Message logger decorator"""
    log_logger = logging.getLogger('Digital Bot')

    async def wrapper(*args, **kwargs):
        message: types.Message = args[0]
        await func(*args)
        log_logger.debug(f'Message {message.text} from @{message.from_user.username} in chat {message.chat.id}')

    return wrapper


def error_log(func):
    """Error logger decorator"""
    error_logger = logging.getLogger('Digital Bot')

    async def wrapper(*args, **kwargs):

        __update: types.update.Update = args[0]
        __exception = args[1]
        __message: types.Message = __update['message']
        error_logger.error(f'Error when trying to send a message to @{__message.from_user.username}!\n'
                           f'User message text: {__message.text}\nError text: {__exception}\n'
                           f'Traceback:\n{traceback.format_exc()}')
        await func(*args, **kwargs)

    return wrapper
