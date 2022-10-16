import os
import logging
import datetime
import argparse
import dotenv

from misc.custom_types import Path


def load_local_vars(path: Path):
    """Create (if necessary) new .env and load vars from"""
    vars_tuple = (
        'echo_mode',  # sqlite
        'bot_token', 'local_bot_host', 'local_bot_port',  # telegram bot token, VM address and port
    )
    path = path + "bot"
    if 'env' not in os.listdir(f'{path}'):
        os.mkdir(f'{path + "env"}')
    path = path + 'env'
    if 'local_vars.env' not in os.listdir(f'{path}'):
        # create local_vars.env
        with open(f'{path + "local_vars.env"}', 'w') as opened_file:
            print('Now, please, type local environment variables')
            for var in vars_tuple:
                new_var = input(f'Enter {var}: ')
                opened_file.write(f'{var} = {new_var}\n')
        # load vars.env
    dotenv.load_dotenv(f'{path + "local_vars.env"}')
    pass


def create_logger(file: str, logger_name: str = None, logger_level: int = 30) -> (logging.Logger, str):
    """Initialization function

    Mostly a procedural function. This creates a logger and determines the path to the root directory.

    :param file: __file__ from script-caller
    :param logger_name: name of logger, if None -- script-caller filename
    :param logger_level: level of logger, default = 30 (WARNING only)
    :return: tuple with [0] -- logger and [1] -- path
    """

    # save the path of current file
    abs_file_path = os.path.abspath(file)
    current_file_path, filename = os.path.split(abs_file_path)

    # save the path of root directory
    path = Path(current_file_path) - 1

    # set default logger_name
    if not logger_name:
        logger_name = 'BSEU schedule'

    # create the directory 'logs' in root dir
    if 'logs' not in os.listdir(path=f'{path}'):
        os.mkdir(str(path + 'logs'))

    trash_cleaner(path + 'logs')

    logging.basicConfig(
        format='%(asctime)s in %(filename)s(%(lineno)d): %(message)s',
        datefmt='%m/%d/%Y %I:%M:%S %p',
        filename='%s/logs/%s.log' % (f'{path}', str(datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S'))),
        level=0  # set file-handler level
    )
    logger = logging.getLogger(logger_name)
    if len(logger.handlers) == 0:
        std_out_handler = logging.StreamHandler()
        std_out_handler.setLevel(logger_level)  # set stdout-handler level
        logger.addHandler(std_out_handler)
    logger.debug('Successfully created "%s" logger' % logger.name)
    return logger, path


def trash_cleaner(path: Path):
    """Clear old .log"""
    __size_in_bytes = 0
    for filename in os.listdir(str(path)):
        __size_in_bytes += os.path.getsize(f'{path + filename}')
    __size_in_m_bytes = __size_in_bytes / 1024 / 1024
    if __size_in_m_bytes < 1024:  # if /logs more than 1 GB
        return None
    file_to_remove = min([_ for _ in os.listdir(str(path))], key=lambda x: os.path.getctime(f'{path + x}'))
    print(file_to_remove)
    os.remove(str(path + file_to_remove))
    trash_cleaner(path)


def get_console_args(version: str = '<Not specified>') -> argparse.Namespace:
    """That functions parse args from command line.

    Also checks for use of the --version or --help flag.

    :return: console_args - Namespace with args, or print them in console and exit().
    """
    parser = argparse.ArgumentParser(description='Digital Spider')

    # optional args
    parser.add_argument('--version', help='Print version info', action='version',
                        version=f'Version {version}')
    parser.add_argument('--verbose', help='Outputs verbose status messages', action='store_true')
    parser.add_argument('--webhook', help='Swith mode from "LoopPolling" to "WebHook"', action='store_true')

    console_args = parser.parse_args()

    return console_args
