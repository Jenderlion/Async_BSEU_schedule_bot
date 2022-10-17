import traceback

from aiogram.utils.exceptions import CantParseEntities
from aiogram.utils.exceptions import ChatNotFound
from aiogram.types import Message
from misc.custom_types import BotInstanceContainer
from misc.custom_types import ScheduleTable
from database.methods.select import get_users
from database.main import User
from keyboards.reply import menu_keyboard
from asyncio.exceptions import TimeoutError as AsyncTimeoutError
import aiohttp


async def send_broadcast(broadcast_text: str):
    tg_bot = BotInstanceContainer().bot
    __users_with_mailing = get_users(__mailing=True)
    __chat_ids = tuple(user.tg_user_id for user in __users_with_mailing)
    for __chat_id in __chat_ids:
        try:
            await tg_bot.send_message(__chat_id, broadcast_text, reply_markup=menu_keyboard())
        except ChatNotFound:
            pass


async def schedule_request(user: User, message: Message, period: str = '3'):
    request_url = 'http://bseu.by/schedule/'
    if user.is_full() is None:
        await message.answer('Чтобы выполнить эту команду, я должен знать всё о тебе (или, хотя бы, группу).'
                             ' Воспользуйся командой /settings, чтобы поделиться со мной.')
        return None
    timeout = aiohttp.ClientTimeout(total=30)
    try:
        async with aiohttp.ClientSession(timeout=timeout) as web_client:
            body = user.request_body()
            body['period'] = period
            resp = await web_client.post(request_url, headers=user.request_headers(), data=body)
            result = await resp.text()
        if 'Расписание не найдено' in result or 'Для получения расписания занятий' in result:
            await message.answer(
                'Расписание не найдено. Если ты уверен, что оно должно быть, обнови данные о своей группе в /settings'
            )
            return None
        __table = result[result.find('<tr>'):]
        __table = __table[:__table.find('</table')]
        table = ScheduleTable(__table, period)
        for day in table.days:
            answer_text_list = [
                f'Расписание на {day.pretty_date()}, {day.week_day} (всего занятий: {len(day.lessons)})',
            ]
            for lesson in day.lessons:
                answer_text_list.append(lesson.pretty_lesson())
            text = '\n\n'.join(answer_text_list)
            try:
                await message.answer(text)
            except CantParseEntities:
                text = f'Расписание на {day.pretty_date()} я спарсить не смог.\n\nМогу предложить вот' \
                       f' это:\n{day.bad_schedule}'
                while True:
                    if '<' in text:
                        to_del = text[text.find('<'):text.find('>') + 1]
                        text = text.replace(to_del, '')
                    else:
                        break
                await message.answer(text.replace('<', '«').replace('>', '»'))
    except AsyncTimeoutError:
        await message.answer(
            'Сайт БГЭУ опять лёг. Попробуй добавить свою группу чуть позже. Если ты можешь зайти на'
            ' http://bseu.by/schedule/, а я — нет, то свяжись с администратором через /help')
