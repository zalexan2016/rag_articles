import logging
import re
from dataclasses import dataclass

from langchain_core.language_models import BaseChatModel
from langchain_core.messages import HumanMessage, SystemMessage

from classes_bot.exceptions import LLMError
from classes_bot.retriever import Retriever
from config import RAG_SYSTEM_PROMPT, RAG_USER_PROMPT

logger = logging.getLogger(__name__)

_IMAGE_IN_ANSWER = re.compile(r"\[image:\s*([^\]]+)\]")
_SOURCE_IN_ANSWER = re.compile(r"\[source:\s*([^\]]+)\]")


@dataclass
class RAGResult:
    answer: str
    sources: list[str]
    image_paths: list[str]


class RAGChain:
    def __init__(self, retriever: Retriever, llm: BaseChatModel):
        self._retriever = retriever
        self._llm = llm

    async def process(self, question: str) -> RAGResult:
        logger.info("Processing question: %s", question)

        chunks = await self._retriever.search(question)

        if not chunks:
            logger.info("No relevant chunks found for question")
            return RAGResult(
                answer="К сожалению, в базе знаний не найдено релевантной информации по вашему вопросу.",
                sources=[],
                image_paths=[],
            )

        context_parts = []
        for chunk in chunks:
            source = chunk.metadata.get("source", "")
            part = f"[source: {source}]\n{chunk.page_content}" if source else chunk.page_content
            context_parts.append(part)
        context = "\n\n".join(context_parts)
        logger.info("Built context from %s chunks", len(chunks))

        messages = [
            SystemMessage(content=RAG_SYSTEM_PROMPT),
            HumanMessage(content=RAG_USER_PROMPT.format(context=context, question=question)),
        ]

        try:
            response = await self._llm.ainvoke(messages)
            answer = response.content
        except Exception as e:
            msg = f"LLM generation failed: {e}"
            raise LLMError(msg) from e

        logger.info("Generated answer of %s chars", len(answer))

        # Если LLM пометила ответ как не требующий источников
        if answer.startswith("[NO_SOURCES]"):
            answer = answer.replace("[NO_SOURCES]", "").strip()
            return RAGResult(answer=answer, sources=[], image_paths=[])

        sources = list(dict.fromkeys(_SOURCE_IN_ANSWER.findall(answer)))

        # Извлекаем только те картинки, которые LLM упомянула в ответе
        image_paths = _IMAGE_IN_ANSWER.findall(answer)
        logger.info("Sources: %s, Images: %s", sources, image_paths)
        # Убираем теги [source: ...] и [image: ...] из текста ответа
        answer = _SOURCE_IN_ANSWER.sub("", answer)
        answer = _IMAGE_IN_ANSWER.sub("", answer).strip()

        logger.info("Extracted %s sources and %s image paths", len(sources), len(image_paths))

        return RAGResult(answer=answer, sources=sources, image_paths=image_paths)
