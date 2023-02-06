import json

import requests
from lxml import html
from functools import cache
from lxml.html import HtmlElement

from aiogram.types import InlineKeyboardButton
from aiogram.types import InlineKeyboardMarkup
from database.main import User


def inline_markup_add_group_info(user: User) -> tuple[str, InlineKeyboardMarkup]:
    """
    Inline Keyboard builder

    Build inline markup for add group info

    :param user: instance of User
    :return:
    """
    keyboard = InlineKeyboardMarkup()
    buttons = []
    data = dict()
    headers = {'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
               'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; rv:11.0) Gecko/20100101 Firefox/11.0'}

    try:
        if user.b_faculty is None:
            resp = requests.get('http://bseu.by/schedule/', timeout=5)
            __trigger = '<select size="0" name="faculty" id="faculty"  class="idnt20"><option value="-1"> </option>'
            __trigger_len = len(__trigger)
            raw_text = resp.text
            raw_table = raw_text[raw_text.find(__trigger) + __trigger_len + 2:]
            raw_table = raw_table[:raw_table.find('</select>')].split('\n')
            faculties = [
                (item[item.find('e="') + 3:item.find('">')], item[item.find('">') + 2:item.find('</')])
                for item in raw_table if item != ''
            ]
            text = 'Выбери факультет:'

            for faculty in faculties:
                buttons.append(InlineKeyboardButton(faculty[1], callback_data=f'group_info b_faculty {faculty[0]}'))

        elif user.b_form is None:
            data['faculty'] = user.b_faculty
            data['__act'] = '__id.22.main.inpFldsA.GetForms'
            resp = requests.post('http://bseu.by/schedule/', data=data, headers=headers, timeout=5)
            answer = eval(resp.text)
            forms = [(item["value"], item["text"]) for item in answer if item['text'] != 'выберите...']
            text = 'Выбери форму обучения:'

            for form in forms:
                buttons.append(InlineKeyboardButton(form[1], callback_data=f'group_info b_form {form[0]}'))

        elif user.b_course is None:
            data['faculty'] = user.b_faculty
            data['form'] = user.b_form
            data['__act'] = '__id.23.main.inpFldsA.GetCourse'
            resp = requests.post('http://bseu.by/schedule/', data=data, headers=headers, timeout=5)
            answer = eval(resp.text)
            courses = [(item["value"], item["text"]) for item in answer if item['text'] != 'выберите...']
            text = 'Выбери курс:'

            for course in courses:
                buttons.append(InlineKeyboardButton(course[1], callback_data=f'group_info b_course {course[0]}'))

        elif user.b_group is None:
            data['faculty'] = user.b_faculty
            data['form'] = user.b_form
            data['course'] = user.b_course
            data['__act'] = '__id.23.main.inpFldsA.GetGroups'
            resp = requests.post('http://bseu.by/schedule/', data=data, headers=headers, timeout=5)
            answer = eval(resp.text)
            groups = [(item["value"], item["text"]) for item in answer if item['text'] != 'выберите...']
            text = 'Выбери группу:'

            for group in groups:
                buttons.append(InlineKeyboardButton(group[1], callback_data=f'group_info b_group {group[0]}'))

        else:
            text = 'Все данные о твоей группе у меня есть :)'
    except requests.exceptions.ReadTimeout:
        text = 'Сайт БГЭУ опять лёг. Попробуй добавить свою группу чуть позже. Если ты можешь зайти на' \
               ' http://bseu.by/schedule/, а я — нет, то свяжись с администратором через /help'

    for button in buttons:
        keyboard.row(button)
    return text, keyboard


def inline_markup_settings(user: User) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup()
    keyboard.row(InlineKeyboardButton(
        f'Обновить основные данные (имя, фамилию и пр.)',
        callback_data='settings bio')
    )
    keyboard.row(InlineKeyboardButton(
        f'Изменить статус рассылки',
        callback_data=f'settings mailing {"0" if user.mailing else "1"}')
    )
    keyboard.row(InlineKeyboardButton(
        f'Обновить данные о группе',
        callback_data='settings group')
    )
    keyboard.row(InlineKeyboardButton(
        f'Изменить скрытые варианты расписания',
        callback_data='settings schedule')
    )
    keyboard.row(InlineKeyboardButton(
        f'Ничего не делать',
        callback_data='settings cancel')
    )
    return keyboard


def inline_markup_hide_schedule(user: User) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup()
    _d_dict = {'today': 'на сегодня', 'tomorrow': 'на завтра', 'week': 'на неделю', 'all': 'на семестр'}
    to_show = []
    hidden = []
    for param_name, param_value in json.loads(user.settings).items():
        if param_value == 1:
            to_show.append(param_name)
        else:
            hidden.append(param_name)
    if to_show:
        for _param in to_show:
            keyboard.row(
                InlineKeyboardButton(
                    f'Скрыть "Расписание {_d_dict[_param]}"',
                    callback_data=f'hide_schedule {_param} 0'
                )
            )
    if hidden:
        for _param in hidden:
            keyboard.row(
                InlineKeyboardButton(
                    f'Отобразить "Расписание {_d_dict[_param]}"',
                    callback_data=f'hide_schedule {_param} 1'
                )
            )
    return keyboard


@cache
def inline_markup_help() -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup()
    keyboard.row(InlineKeyboardButton('Связаться с администратором', callback_data='help request'))
    keyboard.row(InlineKeyboardButton('Сказать "Спасибо"', callback_data='help thanks'))
    return keyboard


def inline_markup_credentials(__target_id: int | str) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup()
    keyboard.row(InlineKeyboardButton('Send contact information', callback_data=f'help credentials {__target_id}'))
    return keyboard


@cache
def inline_markup_schedule(user: User) -> tuple[InlineKeyboardMarkup | None, str | None]:
    _settings: dict = json.loads(user.settings)
    to_show = []
    hidden = []
    for param_name, param_value in _settings.items():
        if param_value == 1:
            to_show.append(param_name)
        else:
            hidden.append(param_name)

    if to_show:
        keyboard = InlineKeyboardMarkup()
        _buttons_dict = {
            'today': InlineKeyboardButton(f'Расписание на сегодня', callback_data='schedule 1'),
            'tomorrow': InlineKeyboardButton(f'Расписание на завтра', callback_data='schedule 2-2'),
            'week': InlineKeyboardButton(f'Расписание на неделю', callback_data='schedule 2'),
            'all': InlineKeyboardButton(f'Расписание на семестр', callback_data='schedule 3'),
        }
        for _var in to_show:
            keyboard.row(_buttons_dict[_var])
    else:
        keyboard = None

    if hidden:
        mes = 'Некоторые варианты скрыты. Чтобы их отобразить, введи /settings или "Настройки"'
    else:
        mes = 'Отображены все варианты. Чтобы скрыть часть из них, введи /settings или "Настройки"'

    return keyboard, mes


def base_markup() -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton('base button', callback_data='base callback'))
    return keyboard
