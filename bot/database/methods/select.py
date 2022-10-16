"""
Database control module. Part "SELECT"
"""


from database.main import User
from database.main import DataBaseEngine
from sqlalchemy.orm import Session
from sqlalchemy.sql import select
from sqlalchemy.engine.base import Engine as ConnectedEngine
from sqlalchemy.orm.session import Session as ConnectedSession
from sqlalchemy.sql.selectable import Select as ConnectedSelect
from sqlalchemy.engine.result import ScalarResult


def get_user(__tg_id: str | int, engine: ConnectedEngine = None) -> User | None:
    """
    Select user.

    Return user with passed ID.

    :param engine: instance of sqlalchemy.engine.base.Engine
    :param __tg_id: user telegram id
    :return: user
    """

    if engine is None:
        engine = DataBaseEngine().engine

    with Session(engine) as __session:
        __session: ConnectedSession
        statement: ConnectedSelect = (select(User).where(User.tg_user_id == __tg_id))
        res: ScalarResult = __session.scalars(statement)
        result_list: list = res.all()
        __session.expunge_all()
        __session.commit()
    if len(result_list) == 1:
        return result_list[0]


def get_users(engine: ConnectedEngine = None, __mailing: bool = None) -> list[User, ...]:
    """Return list with all data-lines"""

    if engine is None:
        engine = DataBaseEngine().engine

    with Session(engine) as __session:
        __session: ConnectedSession
        statement: ConnectedSelect = select(User)
        if __mailing is not None:
            statement = statement.where(User.mailing == __mailing)
        res: ScalarResult = __session.scalars(statement)
        __session.flush()
        result = res.all()
        __session.expunge_all()
        __session.flush()
        __session.commit()
    return result
