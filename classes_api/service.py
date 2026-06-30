from classes_bot.rag_chain import RAGChain, RAGResult


class QueryService:
    def __init__(self, rag_chain: RAGChain):
        self._rag_chain = rag_chain

    async def process(self, question: str) -> RAGResult:
        return await self._rag_chain.process(question)
