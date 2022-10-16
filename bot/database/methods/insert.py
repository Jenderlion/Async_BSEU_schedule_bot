"""
Database control module. Part "INSERT"
"""
import logging

from database.main import User
from database.main import DataBaseEngine
from sqlalchemy.orm import Session
from sqlalchemy.engine.base import Engine as ConnectedEngine
from sqlalchemy.orm.session import Session as ConnectedSession
from sqlalchemy.exc import IntegrityError
from aiogram.types import Message


def add_user(message: Message, engine: ConnectedEngine = None) -> User:
    """
    Use to insert new user.

    The data is retrieved from the message.

    :param engine: instance of sqlalchemy.engine.base.Engine
    :param message: message from user
    :return: user
    """
    if engine is None:
        engine = DataBaseEngine().engine
    try:
        with Session(engine) as __session:
            __session: ConnectedSession
            __id = message.from_id
            __username = message.from_user.username
            __first_name = message.from_user.first_name
            __last_name = message.from_user.last_name
            __new_user = User(
                tg_user_id=__id,
                tg_user_name=__username,
                tg_first_name=__first_name,
                tg_last_name=__last_name,
            )
            __session.add(__new_user)
            __session.flush()
            __session.expunge_all()
            __session.commit()
        return __new_user
    except IntegrityError:
        pass
