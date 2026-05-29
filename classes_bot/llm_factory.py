import logging

from langchain_core.language_models import BaseChatModel
from langchain_openai import ChatOpenAI
from langchain_ollama import ChatOllama

from config import (
    LLM_PROVIDER,
    DEEPSEEK_API_KEY,
    DEEPSEEK_MODEL,
    DEEPSEEK_BASE_URL,
    OLLAMA_BASE_URL,
    OLLAMA_MODEL,
)

logger = logging.getLogger(__name__)


class LLMFactory:
    @staticmethod
    def create() -> BaseChatModel:
        if LLM_PROVIDER == "deepseek":
            logger.info("Creating DeepSeek LLM with model '%s'", DEEPSEEK_MODEL)
            return ChatOpenAI(
                model=DEEPSEEK_MODEL,
                api_key=DEEPSEEK_API_KEY,
                base_url=DEEPSEEK_BASE_URL,
            )
        elif LLM_PROVIDER == "ollama":
            logger.info("Creating Ollama LLM with model '%s'", OLLAMA_MODEL)
            return ChatOllama(
                model=OLLAMA_MODEL,
                base_url=OLLAMA_BASE_URL,
            )
        else:
            raise ValueError("Unknown LLM provider: %s" % LLM_PROVIDER)
