import json
import logging
from dataclasses import dataclass

from langchain_core.language_models import BaseChatModel
from langchain_core.messages import HumanMessage, SystemMessage

from classes_bot.retriever import Retriever
from classes_bot.exceptions import LLMError
from config import RAG_SYSTEM_PROMPT, RAG_USER_PROMPT

logger = logging.getLogger(__name__)


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

        context = "\n\n".join(chunk.page_content for chunk in chunks)
        logger.info("Built context from %s chunks", len(chunks))

        messages = [
            SystemMessage(content=RAG_SYSTEM_PROMPT),
            HumanMessage(content=RAG_USER_PROMPT.format(context=context, question=question)),
        ]

        try:
            response = await self._llm.ainvoke(messages)
            answer = response.content
        except Exception as e:
            raise LLMError("LLM generation failed: %s" % e) from e

        logger.info("Generated answer of %s chars", len(answer))

        sources = list(dict.fromkeys(
            chunk.metadata.get("source", "") for chunk in chunks if chunk.metadata.get("source")
        ))

        image_paths = []
        for chunk in chunks:
            raw = chunk.metadata.get("image_paths", "[]")
            try:
                paths = json.loads(raw) if isinstance(raw, str) else raw
                image_paths.extend(paths)
            except (json.JSONDecodeError, TypeError):
                pass

        logger.info("Extracted %s sources and %s image paths", len(sources), len(image_paths))

        return RAGResult(answer=answer, sources=sources, image_paths=image_paths)
