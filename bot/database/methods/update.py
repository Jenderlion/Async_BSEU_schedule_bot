from database.main import User
from database.main import DataBaseEngine
from sqlalchemy.orm import Session
from sqlalchemy.engine.base import Engine as ConnectedEngine
from sqlalchemy.orm.session import Session as ConnectedSession
from sqlalchemy.orm.query import Query as ConnectedQuery


def update_mailing(__tg_id: str | int, __new_status: str, engine: ConnectedEngine = None) -> int:
    """
    Update user mailing status

    Only for related use

    :param engine: instance of sqlalchemy.engine.base.Engine
    :param __tg_id: user telegram id
    :param __new_status: new mailing status for user
    :return: count of updated users (normal value is 1)
    """
    if engine is None:
        engine = DataBaseEngine().engine
    with Session(engine) as __session:
        __session: ConnectedSession
        __query: ConnectedQuery = __session.query(User).filter(User.tg_user_id == int(__tg_id))
        __update_count = __query.update({'mailing': __new_status})
        __session.commit()
    return __update_count


def update_user_group_info(__tg_id: str | int, __info_tuple: tuple, engine: ConnectedEngine = None) -> int:
    """
    Update user info

    Only for related use

    :param engine: instance of sqlalchemy.engine.base.Engine
    :param __tg_id: user telegram id
    :param __info_tuple: tuple(faculty, form, course, group)
    :return: count of updated users (normal value is 1)
    """
    if engine is None:
        engine = DataBaseEngine().engine
    with Session(engine) as __session:
        __session: ConnectedSession
        __query: ConnectedQuery = __session.query(User).filter(User.tg_user_id == int(__tg_id))
        __update_count = __query.update(
            {
                'b_faculty': __info_tuple[0],
                'b_form': __info_tuple[1],
                'b_course': __info_tuple[2],
                'b_group': __info_tuple[3],
            }
        )
        __session.commit()
    return __update_count


def update_one_user_group_info(
        __tg_id: str | int, __info_name: str, __info_value: str, engine: ConnectedEngine = None
) -> int:
    """
    Update user info

    Only for related use

    :param engine: instance of sqlalchemy.engine.base.Engine
    :param __tg_id: user telegram id
    :param __info_name: attribute name
    :param __info_value: attribute value
    :return: count of updated users (normal value is 1)
    """
    if engine is None:
        engine = DataBaseEngine().engine

    with Session(engine) as __session:
        __session: ConnectedSession
        __query: ConnectedQuery = __session.query(User).filter(User.tg_user_id == __tg_id)
        __update_count = __query.update(
            {
                __info_name: int(__info_value)
            }
        )
        __session.commit()
    return __update_count


def update_user_info(
        __tg_id: str | int, __update_dict: dict, engine: ConnectedEngine = None
) -> int:
    """
    Update user info

    Only for related use

    :param engine: instance of sqlalchemy.engine.base.Engine
    :param __tg_id: user telegram id
    :param __update_dict: values to update
    :return: count of updated users (normal value is 1)
    """
    if engine is None:
        engine = DataBaseEngine().engine

    with Session(engine) as __session:
        __session: ConnectedSession
        __query: ConnectedQuery = __session.query(User).filter(User.tg_user_id == __tg_id)
        __update_count = __query.update(__update_dict)
        __session.commit()
    return __update_count


def delete_user_group_info(__tg_id: str | int, engine: ConnectedEngine = None) -> int:
    """Delete user group info with passed user telegram id. Returns the number of cleared users (normal - 1)"""
    if engine is None:
        engine = DataBaseEngine().engine
    with Session(engine) as __session:
        __session: ConnectedSession
        __query: ConnectedQuery = __session.query(User).filter(User.tg_user_id == int(__tg_id))
        __update_count = __query.update(
            {
                'b_faculty': None,
                'b_form': None,
                'b_course': None,
                'b_group': None,
            }
        )
        __session.commit()
    return __update_count
