import asyncio

from aiogram import Dispatcher

from misc.decorators import *
from keyboards.inline import *
from keyboards.reply import *
from database.methods.select import get_user
from database.main import User
from misc.async_utils import send_broadcast


logger = logging.getLogger('BSEU Schedule')


@log
@start_wrapper
@time_wrapper(2)
async def command_start(message: types.Message, user: User):
    if user.is_full() is not None:
        answer_text = 'Привет! Напиши /help, если забудешь команды :)'
        await message.answer(answer_text, reply_markup=menu_keyboard())
        return None
    answer_text = 'Привет! У тебя нет информации о группе. Сейчас добавим!\n\nКогда закончишь, напиши /help :)'
    await message.answer(answer_text, reply_markup=menu_keyboard())
    await asyncio.sleep(2)
    text, markup = inline_markup_add_group_info(user)
    await message.answer(text, reply_markup=markup)


@log
@time_wrapper(2)
async def command_help(message: types.Message):
    await message.reply(
        'Пользователю доступен следующий набор команд:\n\n'
        '/schedule — узнать расписание\n'
        '/settings — настройки пользователя\n'
        '/help — отправит это меню и предоставит возможность связаться с администратором',
        reply_markup=inline_markup_help()
    )


@log
@time_wrapper(10)
async def command_schedule(message: types.Message):
    await message.answer('Выбирай период:', reply_markup=inline_markup_schedule())


@log
@time_wrapper(1)
async def command_settings(message: types.Message):
    user = get_user(message.from_id)
    answer_text_list = list()
    answer_text_list.append(f'Информация о пользователе:\n@{user.tg_user_name} ({user.tg_user_id})')
    answer_text_list.append(f'Имя: {user.tg_first_name}\nФамилия: {user.tg_last_name}')
    answer_text_list.append(f'Рассылка: {"включена" if user.mailing else "выключена"}')
    answer_text_list.append(f'Данные о группе: {"присутствуют" if user.is_full() else "отсутствуют"}')
    answer_text_list.append(f'Что будем делать?')
    await message.answer('\n\n'.join(answer_text_list), reply_markup=inline_markup_settings(user))


@log
@time_wrapper(1)
async def command_debug(message: types.Message):
    await message.answer(
        f'Debug: {json.dumps(json.loads(str(message)), indent=4)}\n\n{message.text}', reply_markup=base_markup()
    )


@log
async def command_broadcast(message: types.Message):
    if message.from_id != 449808966:
        logger.warning(f'User @{message.from_user.username} (id {message.from_id}) trying to broadcast!!!')
        return None
    message_tuple = message.text.split()
    broadcast_text = ' '.join(message_tuple[1:])
    await send_broadcast(broadcast_text)
    await message.reply('Sent!')


@log
@time_wrapper(1)
async def command__(message: types.Message):
    logger.debug(
        f'Unknown message from user @{message.from_user.username}, chat {message.chat.id}, text: {message.text}'
    )
    await message.reply('Я не знаю такой команды :(', reply_markup=menu_keyboard())


def register_user_handlers(dp: Dispatcher):
    dp.register_message_handler(command_start, commands=('start',))
    dp.register_message_handler(command_help, commands=('help',))
    dp.register_message_handler(command_debug, commands=('debug',))
    dp.register_message_handler(command_schedule, commands=('schedule',))
    dp.register_message_handler(command_settings, commands=('settings',))
    dp.register_message_handler(command_broadcast, commands=('broadcast',))
    dp.register_message_handler(command__)
