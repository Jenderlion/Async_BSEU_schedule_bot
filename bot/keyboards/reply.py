from aiogram.types import ReplyKeyboardMarkup


def menu_keyboard() -> ReplyKeyboardMarkup:
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.row('/schedule')
    keyboard.row('/settings')
    keyboard.row('/help')
    return keyboard
