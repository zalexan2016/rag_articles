import logging
import sys

from aiogram import Bot, Dispatcher

from classes_bot.handlers import MessageHandler
from classes_bot.rag_chain import RAGChain

logger = logging.getLogger(__name__)


class TelegramBot:
    def __init__(self, token: str, rag_chain: RAGChain):
        if not token:
            logger.error("TELEGRAM_BOT_TOKEN is not set")
            sys.exit(1)

        self._bot = Bot(token=token)
        self._dp = Dispatcher()

        handler = MessageHandler(rag_chain)
        self._dp.include_router(handler.router)

    async def start(self) -> None:
        logger.info("Starting Telegram bot polling...")
        await self._dp.start_polling(self._bot)

    async def stop(self) -> None:
        logger.info("Stopping Telegram bot...")
        await self._dp.stop_polling()
        await self._bot.session.close()
