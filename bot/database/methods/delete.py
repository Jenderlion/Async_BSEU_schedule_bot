from sqlalchemy.orm import Session
from sqlalchemy.engine.base import Engine as ConnectedEngine
from sqlalchemy.orm.session import Session as ConnectedSession
from database.main import DataBaseEngine
from .select import get_user


def delete_user(__tg_id: str | int, engine: ConnectedEngine = None):
    """Delete user with passed telegram id"""
    if engine is None:
        engine = DataBaseEngine().engine
    __user = get_user(__tg_id)
    if __user:
        with Session(engine) as __session:
            __session: ConnectedSession
            __session.delete(__user)
            __session.commit()
