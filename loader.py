from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.contrib.fsm_storage.redis import RedisStorage2

from tgbot.config import load_config
from tgbot.models.db_funcs import Database
from tgbot.services.google_docs_funcs import GoogleDocsRedactor


config = load_config(".env")
storage = RedisStorage2() if config.tg_bot.use_redis else MemoryStorage()
bot = Bot(token=config.tg_bot.token, parse_mode="HTML")
dp = Dispatcher(bot, storage=storage)
googledocred = GoogleDocsRedactor()
db = Database()
