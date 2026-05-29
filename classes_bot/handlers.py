import logging
from pathlib import Path

from aiogram import F, Router
from aiogram.enums import ChatAction
from aiogram.types import Message, FSInputFile

from classes_bot.rag_chain import RAGChain, RAGResult
from classes_bot.exceptions import VectorStoreError, LLMError

logger = logging.getLogger(__name__)


class MessageHandler:
    def __init__(self, rag_chain: RAGChain):
        self._rag_chain = rag_chain
        self.router = Router()
        self.router.message.register(self.handle_text, F.text)
        self.router.message.register(self.handle_unsupported)

    async def handle_text(self, message: Message) -> None:
        logger.info("Question from user %s: %s", message.from_user.id, message.text)
        await message.bot.send_chat_action(chat_id=message.chat.id, action=ChatAction.TYPING)

        try:
            result = await self._rag_chain.process(message.text)
            await self._send_response(message, result)
        except VectorStoreError as e:
            logger.error("Vector store error for user %s: %s", message.from_user.id, e)
            await message.answer("⚠️ Произошла временная ошибка сервиса. Попробуйте позже.")
        except LLMError as e:
            logger.error("LLM error for user %s: %s", message.from_user.id, e)
            await message.answer("⚠️ Не удалось сгенерировать ответ. Попробуйте позже.")
        except Exception:
            logger.exception("Unexpected error processing message from user %s", message.from_user.id)
            await message.answer("⚠️ Произошла непредвиденная ошибка. Попробуйте позже.")

    async def handle_unsupported(self, message: Message) -> None:
        await message.answer("Поддерживаются только текстовые вопросы.")

    async def _send_response(self, message: Message, result: RAGResult) -> None:
        text = result.answer
        if result.sources:
            text += "\n\n📚 Источники:"
            for i, source in enumerate(result.sources, 1):
                filename = Path(source).name
                text += f"\n{i}. {filename}"

        await message.answer(text)

        for img_path in result.image_paths:
            path = Path(img_path)
            if path.exists():
                await message.answer_photo(FSInputFile(path))
            else:
                logger.warning("Image file not found: %s", img_path)
