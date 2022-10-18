from aiogram.types import ReplyKeyboardMarkup


def menu_keyboard() -> ReplyKeyboardMarkup:
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.row('Расписание')
    keyboard.row('Настройки')
    keyboard.row('Помощь')
    return keyboard
