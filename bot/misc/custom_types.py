import json
import datetime
import logging
import traceback
import os

from aiogram import Bot


logger = logging.getLogger('BSEU Schedule')


class Path:
    """Focused class for save path to script"""
    root_path = None

    def __init__(self, raw_path: str):
        self.os = 'Linux' if raw_path[0] == '/' else 'Windows' if raw_path[0].isalpha() else 'Unknown OS'

        # OS type
        match self.os:
            case 'Linux':
                self.__sep = '/'
                self.__first = '/'
                self.__last = ''
                self.__path_list = raw_path[1:].split(self.__sep)
            case 'Windows':
                self.__sep = '\\'
                self.__first = ''
                self.__last = ''
                self.__path_list = raw_path.split(self.__sep)
            case _:
                self.__sep = '|'
                self.__first = '<<'
                self.__last = '>>'
                self.__path_list = [raw_path, ]

        self.root = self.__path_list[0]

    def __repr__(self):
        return f'{self.__first}{self.__sep.join(self.__path_list)}{self.__last}'

    def __str__(self):
        return f'{self.__first}{self.__sep.join(self.__path_list)}{self.__last}'

    def __add__(self, other):
        if isinstance(other, str):
            if other.find('\\') != -1:
                other = other.split('\\')
            else:
                other = other.split('/')
        elif isinstance(other, (list, tuple)):
            other = [str(_) for _ in other]
        else:
            raise ValueError('Added part of the path must be <str>, <list> or <tuple>')
        return Path(f'{self}{self.__sep}{self.__sep.join(other)}')

    def __sub__(self, other):
        if isinstance(other, int):
            if other < len(self.__path_list):
                return Path(f'{self.__first}{self.__sep.join(self.__path_list[:-1 * other])}{self.__last}')
            else:
                raise ValueError('You are about to return to more directories than the path specified')
        else:
            raise ValueError('You can only take <int> number of directories and files')

    @classmethod
    def get_root_path(cls):
        if cls.root_path is None:
            abs_file_path = os.path.abspath(__file__)
            current_file_path, filename = os.path.split(abs_file_path)
            cls.root_path = Path(current_file_path) - 1
        return cls.root_path


class BotTimer:
    """Time filter to blocked spamming"""

    __instance = None

    def __new__(cls, *args, **kwargs):
        if cls.__instance is None:
            cls.__instance = super().__new__(cls)
        return cls.__instance

    def __init__(self):
        if 'create_date' not in self.__dict__:
            self.create_date = datetime.datetime.now()
            self.message_time_dict = {}

    def __repr__(self):
        return f'<Bot Timer>, create at {self.create_date}\n{json.dumps(self.message_time_dict, indent=4)}'

    def add_user_timestamp(self, user_id: int, message_timestamp: int):
        self.message_time_dict[user_id] = message_timestamp


class BotInstanceContainer:
    """Saves bot instance"""

    __instance = None

    def __new__(cls, *args, **kwargs):
        if cls.__instance is None:
            cls.__instance = super().__new__(cls)
        return cls.__instance

    def __init__(self, bot: Bot = None):
        if 'bot' not in self.__dict__:
            self.bot = bot


class ScheduleLesson:

    def __init__(self, lesson_list: list):
        try:
            __time = lesson_list.pop(0)
            self.time_string = __time[__time.find('">') + 2:__time.find('</td')]

            if len(lesson_list) > 3:
                __name_data = lesson_list.pop(0)
                lesson_list.pop(0)  # empty item
                __subgroup = lesson_list.pop(0)
                __teacher = lesson_list.pop(0)
                __place = lesson_list.pop(0)

                self.name = __name_data[__name_data.find('">') + 2:__name_data.find('<span')].strip()
                self.data = __name_data[__name_data.find('distype">') + 9:__name_data.find('</span')].strip()
                self.teacher = __teacher[__teacher.find('teacher">') + 9:__teacher.find('</span></td>')].strip()
                self.place = __place[__place.find('">') + 2:__place.find('<')]
                self.subgroup = __subgroup[__subgroup.find('">') + 2:__subgroup.find('</td')]
            else:
                __name_data_t = lesson_list.pop(0)
                __place = lesson_list.pop(0)

                self.name = __name_data_t[__name_data_t.find('">') + 2:__name_data_t.find('<span')].strip()
                self.data = __name_data_t[__name_data_t.find('distype">') + 9:__name_data_t.find('</span')].strip()
                self.teacher = __name_data_t[__name_data_t.find('teacher">') + 9:__name_data_t.find('</span></td>')]\
                    .strip()
                self.place = __place[__place.find('">') + 2:__place.find('</td')]
                self.subgroup = 'вся группа'

            if '<strong>' in self.data:
                self.data = f'({self.data[9:-10]})'

            self.is_full = True
        except Exception as exc:
            logger.error(exc)
            logger.error(traceback.format_exc())

    def __repr__(self):
        _str = f'<ScheduleLesson> {self.name} {self.data} {self.subgroup} at {self.time_string} in {self.place}' \
               f' with {self.teacher}'
        return _str

    def pretty_lesson(self):
        return f'<u>{self.time_string}</u>: {self.name} {self.data} {self.subgroup}\nВедёт {self.teacher} в' \
               f' {self.place}'


class ScheduleDay:

    def __init__(self, day_list: list, period: str):
        self.bad_schedule = '\n<td>'.join(day_list)
        self.__parse_period = period
        if self.__parse_period != '1':
            __row_date = day_list.pop(0)
            __row_date = __row_date[__row_date.find('wday') + 6:__row_date.find('</td>')]
            self.week_day, __date = __row_date.split()
            _d, _m, _y = __date[1:-1].split('.')
            self.date = datetime.datetime(year=int(_y), month=int(_m), day=int(_d))
        else:
            self.date = datetime.datetime.now()
            self.week_day = 'сегодня'
        temp_list = []
        lessons_list = []
        for item in day_list:
            item_list = item.split('\n')
            temp_list.extend(item_list)
            if len(item_list) == 4:
                lessons_list.append(temp_list)
                temp_list = []
        if len(temp_list) > 0:
            lessons_list.append(temp_list)
        self.lessons = [ScheduleLesson(lesson) for lesson in lessons_list]

    def __repr__(self):
        return f'<ScheduleDay> {self.date} {self.week_day}, lessons: {len(self.lessons)}'

    def pretty_date(self):
        __date = self.date
        return f'{__date.day}-{__date.month}-{__date.year}'


class ScheduleTable:

    def __init__(self, input_html_table: str, period: str):
        self.__parse_period = period
        self.__row_cells = input_html_table.split('<tr>')
        self.__row_cells.pop(0)
        title = self.__row_cells.pop(0)
        self.title = title[title.find('<caption>') + 9:title.find('</caption>')]
        self.__row_cells.pop(0)
        day_list = []
        temp_list = [self.__row_cells.pop(0)]
        for item in self.__row_cells:
            if item[0:11] == '<td colspan':
                day_list.append(temp_list)
                temp_list = []
            temp_list.append(item)
        if len(temp_list) > 0:
            day_list.append(temp_list)
        self.days: list[ScheduleDay] = [ScheduleDay(day, period) for day in day_list if len(day) > 0]

    def __repr__(self):
        return f'<ScheduleTable> Days: {len(self.days)}'
