import logging
import os
import sqlalchemy

from sqlalchemy import *
from sqlalchemy.orm import declarative_base


# create tables
Base = declarative_base()


class DataBaseEngine:
    """Saves engine"""
    __instance = None

    def __new__(cls, *args, **kwargs):
        if cls.__instance is None:
            cls.__instance = super().__new__(cls)
        return cls.__instance

    def __init__(self):
        if 'engine' not in self.__dict__:
            self.engine, self.meta = connect_db()

    def __repr__(self):
        return f'<DB Engine>, {self.engine}'

    def create_tables(self):
        self.meta.create_all(self.engine)


class User(Base):
    """Create table"""
    __tablename__ = 'user'
    tg_user_id = Column(INTEGER, primary_key=True)  # tg id
    tg_user_name = Column(VARCHAR(32))  # tg username
    tg_first_name = Column(VARCHAR(64))  # tg first name
    tg_last_name = Column(VARCHAR(64))  # tg last name
    group = Column(VARCHAR(30), default='user')  # group == admin or user
    mailing = Column(BOOLEAN, default=1)  # mailing status where 0 - disable and 1 - enable
    b_faculty = Column(VARCHAR(16), default=None)  # BSEU faculty
    b_form = Column(VARCHAR(16), default=None)  # BSEU form
    b_course = Column(VARCHAR(16), default=None)  # BSEU course
    b_group = Column(VARCHAR(16), default=None)  # BSEU group
    settings = Column(TEXT, default='{"today": 1, "tomorrow": 1, "week": 1, "all": 1}')  # schedule settings

    def __repr__(self):
        return f'<User> ID: {self.tg_user_id} UName: {self.tg_user_name}'

    def group_data(self):
        return self.b_faculty, self.b_form, self.b_course, self.b_group

    def is_full(self):
        return self.b_faculty and self.b_form and self.b_course and self.b_group

    def request_body(self):
        return {
            'faculty': self.b_faculty,
            'form': self.b_form,
            'course': self.b_course,
            'group': self.b_group,
            'tname': '',
            'period': '3',  # day 1, week 2, all 3
            '__act': '__id.25.main.inpFldsA.GetSchedule__sp.7.results__fp.4.main',
        }

    @classmethod
    def request_headers(cls):
        return {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;'
                      'q=0.8,application/signed-exchange;v=b3;q=0.9',
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; rv:11.0) Gecko/20100101 Firefox/11.0'
        }


def connect_db(logger: logging.Logger = None):

    # get base logger
    if logger is None:
        logger = logging.getLogger('Digital Bot')
        if len(logger.handlers) == 0:  # if std handler not added
            std_out_handler = logging.StreamHandler()
            std_out_handler.setLevel(30)  # set stdout-handler level
            logger.addHandler(std_out_handler)

    echo_mode = os.environ.get('echo_mode')
    if echo_mode is None:
        echo_mode = False

    # create DB
    logger.debug('Creating DB engine...')
    connect_string = "sqlite:///scheduler_db.sqlite"
    db_engine = sqlalchemy.create_engine(connect_string, echo=eval(echo_mode))
    meta = sqlalchemy.MetaData()
    Base.metadata.create_all(db_engine)
    logger.debug('Connected to DB.')
    return db_engine, meta


def create_engine():
    # saves engine
    DataBaseEngine()
