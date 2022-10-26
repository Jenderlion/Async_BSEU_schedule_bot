"""
Wunder Digital Bot.
Implemented functionality:
- updating invalid tokens

Webhook-server in development!!!
Start this script only through start.sh or start.cmd
"""


import logging
import os
import json

import uvicorn
from fastapi import FastAPI

from aiogram.utils import executor
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage

from filters import register_all_filters
from handlers import register_all_handlers
from database import create_engine

from misc.util import load_local_vars
from misc.util import create_logger
from misc.util import get_console_args
from misc.custom_types import Path
from misc.custom_types import BotInstanceContainer

from apscheduler.schedulers.asyncio import AsyncIOScheduler


# create app
app = FastAPI()


# globals
manual_debug = False

console_args = get_console_args()
if console_args.verbose:
    logger_level = 0
else:
    logger_level = 30
if manual_debug:
    logger_level = 0
    pass

logger, path = create_logger(__file__, logger_name='BSEU Schedule', logger_level=logger_level)
logger: logging.Logger
path: Path

load_local_vars(path)
tg_bot = Bot(token=os.environ.get("bot_token"), parse_mode='HTML')
BotInstanceContainer(tg_bot)  # save Bot instance in data-class
dp = Dispatcher(tg_bot, storage=MemoryStorage())
__host = os.environ['local_bot_host']  # for webhook
__port = os.environ['local_bot_port']  # for webhook


# app funcs
@app.on_event('startup')
async def app_startup():

    webhook_info = await tg_bot.get_webhook_info()
    print(webhook_info)


@app.post('')
async def __set__webhook(update: dict):
    __update = types.Update(**update)
    __json = json.dumps(update, indent=4)
    print(json)
    pass


# bot funcs
async def __on_start_up(disp: Dispatcher) -> None:
    register_all_filters(dp)
    register_all_handlers(dp)

    create_engine()
    schedule()


async def __on_shut_down(disp: Dispatcher) -> None:
    pass


def schedule() -> None:
    """Schedule create"""
    # scheduler = AsyncIOScheduler()
    # scheduler.add_job(check_vars, 'interval', seconds=3600, )
    # scheduler.start()


if __name__ == '__main__':

    if console_args.webhook:
        # todo: webhook server
        print('IN DEVELOPMENT!!!')
        uvicorn.run('main:app', host=__host, port=int(__port), reload=True)
    else:
        logger.warning('Bot start in Long polling mode.')
        executor.start_polling(dp, skip_updates=True, on_startup=__on_start_up, on_shutdown=__on_shut_down)

else:

    async def set_wh():
        await tg_bot.set_webhook(__host)
    app_startup()
    executor.start_webhook(
        dispatcher=dp,
        webhook_path='',
        on_startup=__on_start_up,
        on_shutdown=__on_shut_down,
        skip_updates=True,
        host=__host,
        port=__port,
    )
