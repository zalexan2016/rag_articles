import asyncio
import logging
import signal

import uvicorn

from classes_api.app import create_app
from config import API_HOST, API_PORT
from core_rag.rag_chain import RAGChain

logger = logging.getLogger(__name__)


class APIServer:
    def __init__(self, rag_chain: RAGChain):
        self._app = create_app(rag_chain)
        self._server: uvicorn.Server | None = None

    async def run(self) -> None:
        config = uvicorn.Config(self._app, host=API_HOST, port=API_PORT, log_level="info")
        self._server = uvicorn.Server(config)
        loop = asyncio.get_event_loop()
        for sig in (signal.SIGINT, signal.SIGTERM):
            loop.add_signal_handler(sig, self._handle_signal)
        logger.info("Starting API server on %s:%s", API_HOST, API_PORT)
        await self._server.serve()

    def _handle_signal(self) -> None:
        if self._server:
            self._server.should_exit = True
