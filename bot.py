import asyncio
import logging

from tgbot.config import load_config

from tgbot.handlers.acquaintance import register_acquaintance_handlers
from tgbot.handlers.echo import register_echo
from tgbot.handlers.faq import register_faq_handlers
from tgbot.handlers.map import register_map_handlers
from tgbot.handlers.registration import register_registration_handlers
from tgbot.handlers.schedule import register_schedule_handlers

from loader import db, bot, dp
from tgbot.models import db_funcs

logger = logging.getLogger(__name__)


def register_all_handlers(dp):
    register_registration_handlers(dp)
    register_acquaintance_handlers(dp)
    register_map_handlers(dp)
    register_schedule_handlers(dp)
    register_faq_handlers(dp)

    register_echo(dp)


async def main():
    logging.basicConfig(
        level=logging.INFO,
        format=u'%(filename)s:%(lineno)d #%(levelname)-8s [%(asctime)s] - %(name)s - %(message)s',
    )
    logger.info("Starting bot")
    config = load_config(".env")

    bot['config'] = config

    register_all_handlers(dp)

    try:
        await db_funcs.on_startup(db)
        await dp.start_polling()
    finally:
        await dp.storage.close()
        await dp.storage.wait_closed()
        await bot.session.close()


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.error("Bot stopped!")
