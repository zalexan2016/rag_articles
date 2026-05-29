import logging

from langchain_core.language_models import BaseChatModel
from langchain_openai import ChatOpenAI
from langchain_ollama import ChatOllama

from config import LLM_API_KEY, LLM_MODEL, LLM_BASE_URL

logger = logging.getLogger(__name__)


class LLMFactory:
    @staticmethod
    def create() -> BaseChatModel:
        if LLM_API_KEY:
            logger.info("Creating OpenAI-compatible LLM with model '%s' at '%s'", LLM_MODEL, LLM_BASE_URL)
            return ChatOpenAI(
                model=LLM_MODEL,
                api_key=LLM_API_KEY,
                base_url=LLM_BASE_URL,
            )
        else:
            logger.info("Creating Ollama LLM with model '%s' at '%s'", LLM_MODEL, LLM_BASE_URL)
            return ChatOllama(
                model=LLM_MODEL,
                base_url=LLM_BASE_URL,
            )
