from aiogram import Dispatcher

from database.methods.update import update_user_info
from database.methods.update import update_one_user_group_info
from database.methods.update import delete_user_group_info
from misc.decorators import *
from misc.custom_types import BotInstanceContainer
from misc.async_utils import schedule_request
from keyboards.inline import inline_markup_add_group_info
from keyboards.inline import inline_markup_credentials


logger = logging.getLogger('BSEU Schedule')

@error_log
async def error_handler(*args, ** kwargs):
    tg_bot = BotInstanceContainer().bot
    message_text = f'Except in WunderBot!\n{args}\n{kwargs}'
    message_text = message_text.replace('<', 'Instance: →').replace('>', '←')
    await tg_bot.send_message(449808966, message_text)
    return True


@callback_wrapper
async def callback__(*args, ** kwargs):
    tg_bot = BotInstanceContainer().bot
    message_text = f'Unknown Callback Query!\n{args}\n{kwargs}'
    message_text = message_text.replace('<', 'Instance: →').replace('>', '←')
    message_text = f'<code>{message_text}</code>'
    await tg_bot.send_message(chat_id=449808966, text=message_text)


@callback_wrapper
async def callback_group_info(*args, ** kwargs):
    callback: types.CallbackQuery = args[0]
    bot_message: types.Message = callback.message
    callback_tuple = callback.data.split()
    if len(callback_tuple) != 3:
        await bot_message.answer('Что-то пошло не так. Свяжись с администратором, пожалуйста')
        return None
    if callback_tuple[1] not in ('b_faculty', 'b_form', 'b_course', 'b_group'):
        await bot_message.answer('Какие-то странные данные... Может быть, ты пытаешься их подменить?')
        return None
    try:
        update_one_user_group_info(callback.from_user.id, callback_tuple[1], callback_tuple[2])
        new_text, new_markup = inline_markup_add_group_info(user=get_user(callback.from_user.id))
        await bot_message.answer(new_text, reply_markup=new_markup)
    except Exception as exc:
        print(type(exc))
        print(exc)


@callback_wrapper
async def callback_schedule(*args, **kwargs):
    callback: types.CallbackQuery = args[0]
    bot_message: types.Message = callback.message
    callback_tuple = callback.data.split()
    if callback_tuple[1] in ('1', '2', '3'):
        user = get_user(callback.from_user.id)
        await schedule_request(user, bot_message, callback_tuple[1])
        return None
    await bot_message.answer('От тебя приходят странные данные. Ты их не менял?')


@callback_wrapper
async def callback_settings(*args, **kwargs):
    callback: types.CallbackQuery = args[0]
    bot_message: types.Message = callback.message
    callback_tuple = callback.data.split()

    match callback_tuple[1]:
        case 'bio':
            update_user_info(
                callback.from_user.id,
                {
                    'tg_user_name': callback.from_user.username,
                    'tg_first_name': callback.from_user.first_name,
                    'tg_last_name': callback.from_user.last_name,
                }
            )
        case 'mailing':
            update_user_info(
                callback.from_user.id,
                {
                    'mailing': True if callback_tuple[2] == '1' else False,
                }
            )
        case 'group':
            delete_user_group_info(callback.from_user.id)
            user = get_user(callback.from_user.id)
            text, markup = inline_markup_add_group_info(user)
            await bot_message.answer(text, reply_markup=markup)
        case 'cancel':
            pass
        case _:
            await bot_message.answer('От тебя приходят странные данные. Ты их не менял?')


@callback_wrapper
async def callback_help(*args, **kwargs):
    callback: types.CallbackQuery = args[0]
    bot_message: types.Message = callback.message
    callback_tuple = callback.data.split()
    tg_bot = BotInstanceContainer().bot

    match callback_tuple[1]:
        case 'request':
            await tg_bot.send_message(
                449808966,
                f'User @{callback.from_user.username} ({callback.from_user.id}) needs help!',
                reply_markup=inline_markup_credentials(callback.from_user.id)
            )
        case 'credentials':
            await tg_bot.send_message(callback_tuple[2], 'Администратор просит Вас связаться с ним\n\n@jenderlion')
        case 'thanks':
            await bot_message.answer('Поблагодарить создателя можно следующими способами:')
            try:
                with open('img/oplati_qr.png', 'rb') as opened_file:
                    await tg_bot.send_photo(callback.from_user.id, opened_file, 'Через приложение "Оплати" по QR-коду:')
            except Exception as exc:
                logger.error(exc)
                logger.error(traceback.format_exc())
            await bot_message.answer('Через кошельки:\n\n'
                                     'USDT/USDC (сеть <u>TRC20</u>): TFCmqwoMLc6wn7JByk3zsVyrUo7yN5okK3\n'
                                     'ETH (сеть <u>ERC20</u>): 0x6b4c1924fb6d8d0d1d919357bdc7f6952ee753d6\n'
                                     'BTC (сеть <u>Bitcoin</u>): 3LgofPSzhWPGY89MxVmfS555S6qRi3PhHZ')
        case _:
            await bot_message.answer('От тебя приходят странные данные. Ты их не менял?')


def register_other_handlers(dp: Dispatcher) -> None:

    dp.register_errors_handler(error_handler)

    dp.register_callback_query_handler(callback_group_info, lambda c: c.data.split()[0] == 'group_info')
    dp.register_callback_query_handler(callback_schedule, lambda c: c.data.split()[0] == 'schedule')
    dp.register_callback_query_handler(callback_settings, lambda c: c.data.split()[0] == 'settings')
    dp.register_callback_query_handler(callback_help, lambda c: c.data.split()[0] == 'help')
    dp.register_callback_query_handler(callback__, lambda c: True)
