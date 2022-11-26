import asyncio
import os
import random
import sys

import speech_recognition as sr

from aiogram.utils.exceptions import CantParseEntities
from aiogram.utils.exceptions import ChatNotFound
from aiogram.utils.exceptions import BotBlocked
from aiogram.types import Message
from aiogram.types.file import File
from misc.custom_types import BotInstanceContainer, Path
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
        _count = 0
        while _count < 3:
            _count += 1
            try:
                await tg_bot.send_message(__chat_id, broadcast_text, reply_markup=menu_keyboard())
                break
            except ChatNotFound:
                break
            except BotBlocked:
                await asyncio.sleep(random.random() * 5)
            except Exception as exc:
                await tg_bot.send_message(
                    449808966, f"C = {_count}\n{str(type(exc)).replace('<', '«').replace('>', '»')}"
                )
                break


async def schedule_request(user: User, message: Message, period: str = '3'):
    if period == '2-2':
        period = '2'
        _tomorrow = True
    else:
        _tomorrow = False
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
        if _tomorrow:
            table.days = [table.days[1], ]
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


async def voice_handler(file: File) -> str:

    root_dir = Path.get_root_path()
    files_dir = root_dir + 'voices'

    if 'voices' not in os.listdir(str(root_dir)):
        os.mkdir(str(files_dir))

    __size_in_bytes = 0
    for filename in os.listdir(str(files_dir)):
        __size_in_bytes += os.path.getsize(f'{files_dir + filename}')
    __size_in_m_bytes = __size_in_bytes / 1024 / 1024

    while __size_in_m_bytes > 64:
        file_to_remove = min(
            [_ for _ in os.listdir(str(files_dir))], key=lambda x: os.path.getctime(f'{files_dir + x}')
        )
        __size_in_bytes -= os.path.getsize(str(files_dir + file_to_remove))
        __size_in_m_bytes = __size_in_bytes / 1024 / 1024
        os.remove(str(files_dir + file_to_remove))

    tg_bot = BotInstanceContainer().bot
    file_path = files_dir + str(file.file_unique_id + '.oga')
    wav_path = file_path - 1
    wav_path += f'{file.file_unique_id}.wav'
    await tg_bot.download_file_by_id(file.file_id, destination=str(file_path))

    if sys.platform != 'win32':
        os.system(f'ffmpeg -i {file_path} {wav_path}')
    else:
        wav_path = wav_path - 1
        wav_path = wav_path + 'AgADLCMAAllIyEo.wav'

    r = sr.Recognizer()
    try:
        with sr.AudioFile(str(wav_path)) as source:
            audio_data = r.record(source)
            text = r.recognize_google(audio_data, language='ru-RU')
            text = text.capitalize()
    except Exception as exc:
        text = 'Очень интересно, но я ничего не понял'

    return text
